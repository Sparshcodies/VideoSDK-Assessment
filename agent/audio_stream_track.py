import asyncio
from fractions import Fraction
import threading
import time
import traceback
from typing import Iterator, Optional
from av import AudioFrame
from vsaiortc.mediastreams import AudioStreamTrack
import numpy as np


AUDIO_PTIME = 0.02


def build_audio_frame(chunk: bytes) -> AudioFrame:
    data = np.frombuffer(chunk, dtype=np.int16)
    data = data.reshape(-1, 1)
    audio_frame = AudioFrame.from_ndarray(data.T, format="s16", layout="mono")
    return audio_frame

class MediaStreamError(Exception):
    pass


class CustomAudioStreamTrack(AudioStreamTrack):
    def __init__(
        self, loop, handle_interruption: Optional[bool] = True,
    ):
        super().__init__()
        self.loop = loop
        self._start = None
        self._timestamp = 0

        # frame buffer to send frames in videosdk meeting
        self.frame_buffer = []

        # Audio data buffer to store incoming audio
        self.audio_data_buffer = bytearray()

        # Audio frame properties
        self.frame_time = 0
        self.sample_rate = 24000
        self.channels = 1
        self.sample_width = 2
        self.time_base_fraction = Fraction(1, self.sample_rate)
        self.samples = int(AUDIO_PTIME * self.sample_rate)
        self.chunk_size = int(self.samples * self.channels * self.sample_width)

        self._process_audio_task_queue = asyncio.Queue()
        self._process_audio_thread = threading.Thread(target=self.process_incoming_audio)
        self._process_audio_thread.daemon = True
        self._process_audio_thread.start()

        self.handle_interruption = handle_interruption
        self.skip_next_chunk = False

    def interrupt(self):
        if self.handle_interruption == True:
          length = len(self.frame_buffer)
          self.frame_buffer.clear()
          while not self._process_audio_task_queue.empty():
              self.skip_next_chunk = True
              self._process_audio_task_queue.get_nowait()
              self._process_audio_task_queue.task_done()
              
          if length>0:
              self.skip_next_chunk = True

    def add_new_bytes(self, bytes: Iterator[bytes]):
        # self.interrupt()
        self._process_audio_task_queue.put_nowait(bytes)

    def process_incoming_audio(self):
        while True:
            try:
                if (self._process_audio_task_queue.empty()):
                    while True:
                        if len(self.frame_buffer) > 0:
                            time.sleep(0.5)
                            continue
                        print("Interviewer is not speaking")
                        break
            except Exception as e:
                print("Error while updating character state")

            try:
                audio_data_stream = asyncio.run_coroutine_threadsafe(
                   self._process_audio_task_queue.get(), self.loop
                ).result()
                for audio_data in audio_data_stream:
                    try:
                        self.audio_data_buffer += audio_data
                        print(f"Received audio data: {len(audio_data)} bytes", len(self.audio_data_buffer))
                        while len(self.audio_data_buffer) > self.chunk_size:
                            chunk = self.audio_data_buffer[: self.chunk_size]
                            self.audio_data_buffer = self.audio_data_buffer[
                                self.chunk_size :
                            ]

                            # bytes to av.AudioFrame
                            audio_frame = build_audio_frame(chunk)
                            
                            # append frame into frame buffer
                            self.frame_buffer.append(audio_frame)
                            print("Interviewer is Speaking")
                    except Exception as e:
                        traceback.print_exc()
                        print("Error while putting audio data stream", e)
                        exit(0)
            except Exception as e:
                traceback.print_exc()
                print("Error while processing audio", e)

    def next_timestamp(self):
        # Compute the next timestamp for the audio frame
        pts = int(self.frame_time)
        time_base = self.time_base_fraction
        self.frame_time += self.samples
        # self.chunk_size / self.channels / self.sample_width
        return pts, time_base

    # based on ptime videosdk call recv method to get new frame
    async def recv(self) -> AudioFrame:
        try:
            if self.readyState != "live":
                raise MediaStreamError

            if self._start is None:
                self._start = time.time()
                self._timestamp = 0
            else:
                self._timestamp += self.samples

            wait = self._start + (self._timestamp / self.sample_rate) - time.time()

            if wait > 0:
                await asyncio.sleep(wait)

            pts, time_base = self.next_timestamp()

            if len(self.frame_buffer) > 0:
                frame = self.frame_buffer.pop(0)
            else:
                frame = AudioFrame(format="s16", layout="mono", samples=self.samples)
                for p in frame.planes:
                    p.update(bytes(p.buffer_size))

            frame.pts = pts
            frame.time_base = time_base
            frame.sample_rate = self.sample_rate
            return frame
        except Exception as e:
            traceback.print_exc()
            print("error while creating tts->rtc frame", e)

