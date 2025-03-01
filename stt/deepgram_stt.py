from asyncio.log import logger
import traceback
from typing import Dict, List
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    ListenWebSocketClient
)
from asyncio import AbstractEventLoop, Task
import numpy as np
from datetime import datetime, timezone
from vsaiortc.mediastreams import MediaStreamError
from videosdk import Stream
from stt.stt import STT
from intelligence.intelligence import Intelligence

LEARNING_RATE = 0.1
LENGTH_THRESHOLD = 5
SMOOTHING_FACTOR = 3
BASE_WPM = 150.0
VAD_THRESHOLD_MS = 25
UTTERANCE_CUTOFF_MS = 300

class DeepgramSTT(STT):

    def __init__(
        self,
        loop: AbstractEventLoop,
        api_key,
        language,
        intelligence:Intelligence
    ) -> None:
        self.loop = loop

        self.vad_threshold_ms: int = VAD_THRESHOLD_MS
        self.utterance_cutoff_ms: int = UTTERANCE_CUTOFF_MS
        self.model = "nova-2"
        self.speed_coefficient: float = 1.0
        self.wpm_0 = BASE_WPM * self.speed_coefficient
        self.wpm = self.wpm_0
        self.speed_coefficient = self.speed_coefficient

        self.buffer = ""
        self.words_buffer = []

        self.deepgram_client = DeepgramClient(
            api_key=api_key,
            config=DeepgramClientOptions(options={"keepalive": True}),
        )
        self.language = language
        self.deepgram_connections:Dict[str,ListenWebSocketClient] = {}
        self.audio_tasks:Dict[str, Task] = {}

        self.finalize_called: Dict[str, bool] = {}

        # intelligence
        self.intelligence = intelligence
        self.pubsub = None
    
    def set_pubsub(self, pubsub):
        self.pubsub = pubsub

    def start(self, peer_id: str, peer_name: str, stream:Stream):

        def on_deepgram_stt_text_available(connection, result, **kwargs):
            self.on_deepgram_stt_text_available(peer_id=peer_id, peer_name=peer_name, result=result)

        def on_utterance_end(connection, utterance_end, **kwargs):
            self.on_utterance_end(peer_id=peer_id, peer_name=peer_name)
        
        def on_open(connection, open, **kwargs):
            self.on_open(peer_id=peer_id, peer_name=peer_name)

        def on_metadata(connection, metadata, **kwargs):
            self.on_metadata(peer_id=peer_id, peer_name=peer_name, metadata=metadata)

        def on_speech_started(connection, speech_started, **kwargs):
            self.on_speech_started(peer_id=peer_id, peer_name=peer_name)
            
        def on_close(connection, close, **kwargs):
            self.on_close(peer_id=peer_id, peer_name=peer_name)

        def on_error(connection, error, **kwargs):
            self.on_error(peer_id=peer_id, peer_name=peer_name, error=error)

        def on_unhandled(connection, unhandled, **kwargs):
            self.on_unhandled(peer_id=peer_id, peer_name=peer_name, unhandled=unhandled)

        deepgram_options = LiveOptions(
            model=self.model,
            language=self.language,
            smart_format=True,
            encoding="linear16",
            channels=2,
            sample_rate=48000,
            interim_results=True,
            vad_events=True,
            filler_words=True,
            punctuate=True,
            endpointing=int(self.vad_threshold_ms * (1 / self.speed_coefficient)),
            utterance_end_ms=max(
                int(self.utterance_cutoff_ms * (1 / self.speed_coefficient)), 1000
            ),
            no_delay=True,
        )
        deepgram_connection = self.deepgram_client.listen.live.v("1")

        deepgram_connection.on(
            LiveTranscriptionEvents.Transcript, on_deepgram_stt_text_available
        )
        deepgram_connection.on(LiveTranscriptionEvents.Open, on_open)
        deepgram_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        deepgram_connection.on(
            LiveTranscriptionEvents.SpeechStarted, on_speech_started
        )
        deepgram_connection.on(
            LiveTranscriptionEvents.UtteranceEnd, on_utterance_end
        )
        deepgram_connection.on(LiveTranscriptionEvents.Close, on_close)
        deepgram_connection.on(LiveTranscriptionEvents.Error, on_error)
        deepgram_connection.on(
            LiveTranscriptionEvents.Unhandled, on_unhandled
        )
        deepgram_connection.start(
            deepgram_options,
            addons={"no_delay": "true"},
        )

        self.deepgram_connections[peer_id] = deepgram_connection

        self.finalize_called[peer_id] = False
        self.task = self.loop.create_task(
            self.add_peer_stream(
                stream=stream, peer_id=peer_id, peer_name=peer_name
            )
        )

    def stop(self, peer_id):
        if peer_id in self.deepgram_connections:
            print("stop peer audio connection", peer_id)
            self.deepgram_connections[peer_id].finalize()
            self.deepgram_connections[peer_id].finish()
            self.finalize_called[peer_id] = True    
            del self.deepgram_connections[peer_id]

    def get_usage(self):
        current_usage = self.usage
        self.usage = 0
        return current_usage

    async def add_peer_stream(self, stream: Stream, peer_id: str, peer_name: str):
        try:
            track = stream.track

            while not self.finalize_called[peer_id]:
                frame = await track.recv()
                audio_data = frame.to_ndarray()
                pcm_frame = audio_data.flatten().astype(np.int16).tobytes()
                self.deepgram_connections[peer_id].send(pcm_frame)
        except Exception as e:
            traceback.print_exc()
            print("Error while sending audio to STT Server", e)

    def on_deepgram_stt_text_available(self, peer_id, peer_name, result):
        try:
            top_choice = result.channel.alternatives[0]

            if len(top_choice.transcript) == 0:
                return

            # Check for transcript, confidentce and
            if (
                top_choice.transcript
                and top_choice.confidence > 0.0
                and result.is_final
            ):
                # Get words
                words = top_choice.words
                if words:
                    # Add words to buffer
                    self.words_buffer.extend(words)

                self.buffer = f"{self.buffer} {top_choice.transcript}"
                print(f"Buffer {self.buffer}")

            if (self.buffer and self.is_endpoint(result)) or self.finalize_called[peer_id]:

                duration_seconds = self.calculate_duration(self.words_buffer)
                # print("Duration seconds", duration_seconds)

                if duration_seconds is not None:
                    wpm = (
                        60 * len(self.buffer.split()) / duration_seconds
                        if duration_seconds
                        else None
                    )
                    print("WPM", wpm)
                    if wpm is not None:
                        self.update_speed_coefficient(wpm=wpm, message=self.buffer)

                self.produce_text(self.buffer, peer_name=peer_name, is_final=True)
                

            if top_choice.transcript and top_choice.confidence > 0.0:
                if not result.is_final:
                    interim_message = f"{self.buffer} {top_choice.transcript}"
                else:
                    interim_message = self.buffer

                # if interim_message:
                #     self.produce_text(interim_message, peer_name=peer_name,is_final=False)

        except Exception as e:
            print("Error while transcript processing", e)

    def on_open(self, peer_id, peer_name):
        print(f"Connection Open")

    def on_metadata(self, peer_id, peer_name, metadata):
        print(f"Metadata: {metadata}")

    def on_speech_started(self, peer_id, peer_name):
        # print(f"[{peer_name}] Speech Started")
        pass

    def on_utterance_end(self, peer_id, peer_name):
        print(f"Utterance End")
        # self.produce_text(self.buffer, peer_name=peer_name, is_final=True)

    def on_close(self, peer_id, peer_name):
        print(f"Connection Closed")

    def on_error(self, peer_id, peer_name, error):
        print(f"Handled Error: {error}")

    def on_unhandled(self, peer_id, peer_name, unhandled):
        print(f"Unhandled Websocket Message: {unhandled}")

    def now(self) -> datetime:
        return datetime.now(tz=timezone.utc)

    def is_endpoint(self, deepgram_response):
        is_endpoint = (deepgram_response.channel.alternatives[0].transcript) and (
            deepgram_response.speech_final
        )
        return is_endpoint

    def calculate_duration(self, words: List[dict]) -> float:
        if len(words) == 0:
            return 0.0
        return words[-1]["end"] - words[0]["start"]

    def produce_text(self, text: str, peer_name:str, is_final: bool = False):
        try:
            if is_final and text:
                # peer final message after speech
                print(f"[{peer_name}]:", text)
                if self.pubsub is not None:
                    # publish in meeting
                    self.pubsub(message=f"[{peer_name}]: {text}")
                self.intelligence.generate(text=text, sender_name=peer_name)
                self.buffer = ""
                self.words_buffer = []

            if text:
                # print(f"[{peer_name}]:", text)
                pass
        except Exception as e:
            print("Error while producing text", e)

    def update_speed_coefficient(self, wpm: int, message: str):
        if wpm is not None:
            length = len(message.strip().split())
            p_t = min(
                1,
                LEARNING_RATE
                * ((length + SMOOTHING_FACTOR) / (LENGTH_THRESHOLD + SMOOTHING_FACTOR)),
            )
            self.wpm = self.wpm * (1 - p_t) + wpm * p_t
            self.speed_coefficient = self.wpm / BASE_WPM
            logger.info(f"Set speed coefficient to {self.speed_coefficient}")