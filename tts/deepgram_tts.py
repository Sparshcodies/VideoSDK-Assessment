import json
import threading
import asyncio
from typing import Iterator, Union
from websockets.sync.client import connect
from tts.tts import TTS
from videosdk.stream import MediaStreamTrack


class DeepgramTTS(TTS):
    def __init__(self, api_key: str, output_track: MediaStreamTrack):
        base_url = f"wss://api.deepgram.com/v1/speak?encoding=linear16&sample_rate=24000&&model=aura-stella-en"
        print(f"Connecting to {base_url}")
        self.output_track = output_track
        self.api_key = api_key
        self._socket = None
        self._exit = threading.Event()

        try:
            self._socket = connect(
                base_url, additional_headers={"Authorization": f"Token {self.api_key}"}
            )
            print("WebSocket connection established.")
        except Exception as e:
            print(f"Failed to connect to WebSocket: {e}")
            return

        async def receiver():
            try:
                while True:
                    if self._socket is None or self._exit.is_set():
                        break

                    message = self._socket.recv()
                    if message is None:
                        continue

                    if isinstance(message, str):
                        print(f"Received message: {message}")
                    elif isinstance(message, bytes):
                        print(f"Received bytes: {len(message)} bytes")
                        self.output_track.add_new_bytes(iter([message]))  # Send entire byte chunk

            except Exception as e:
                print(f"receiver: {e}")

        self._receiver_thread = threading.Thread(target=asyncio.run, args=(receiver(),))
        self._receiver_thread.start()

    def generate(self, text: Union[str, Iterator[str]]):
        if self._socket is None:
            print("WebSocket is not connected.")
            return

        if isinstance(text, str):
            print(f"Sending: {text}")
            self._socket.send(json.dumps({"type": "Speak", "text": text}))
        elif isinstance(text, Iterator):
            for t in text:
                print(f"Sending: {t}")
                self._socket.send(json.dumps({"type": "Speak", "text": t}))
        else:
            print("Invalid input: text must be a str or an Iterator of str.")

    def close(self):
        self._exit.set()
        if self._socket:
            self._socket.close()
        self._receiver_thread.join()