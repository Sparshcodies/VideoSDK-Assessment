import asyncio
from videosdk import (
    VideoSDK,
    Meeting,
    Participant,
    MeetingEventHandler,
    ParticipantEventHandler,
)

# types
from videosdk import MeetingConfig, Stream, PubSubPublishConfig
from intelligence.intelligence import Intelligence
from stt.stt import STT
from videosdk.stream import MediaStreamTrack


class AIInterviewer:
    def __init__(self, loop:asyncio.AbstractEventLoop, audio_track: MediaStreamTrack, stt: STT, intelligence: Intelligence):
        self.name = "Bucky"
        self.loop = loop
        self.meeting: Meeting = None
        self.stt: STT = stt
        self.intelligence: Intelligence = intelligence
        self.audio_track = audio_track

    async def join(self, meeting_id: str, token: str):
        print(meeting_id, token)
        meeting_config = MeetingConfig(
            meeting_id=meeting_id,
            name=self.name,
            mic_enabled=True,
            webcam_enabled=False,
            custom_microphone_audio_track=self.audio_track,
            token=token,
        )
        self.meeting = VideoSDK.init_meeting(**meeting_config)

        self.meeting.add_event_listener(MyMeetingEventListener(stt=self.stt))

        await self.meeting.async_join()

        self.stt.set_pubsub(pubsub=self.publish_message)
        self.intelligence.set_pubsub(pubsub=self.publish_message)

    def publish_message(self, message):
        self.loop.create_task(self.meeting.pubsub.publish(
            PubSubPublishConfig(
                topic="CHAT",
                message=message,
            )
        ))

    async def leave(self):
        print("leaving meeting...")
        self.meeting.leave()


class MyMeetingEventListener(MeetingEventHandler):
    def __init__(self, stt: STT):
        super().__init__()
        self.stt = stt
        print("Meeting :: EventListener initialized")

    def on_meeting_state_change(self, data):
        print("Meeting state changed", data)

    def on_meeting_joined(self, data):
        print("Meeting joined")

    def on_meeting_left(self, data):
        print("Meeting left")

    def on_participant_joined(self, participant: Participant):
        print(f"Participant {participant.display_name} joined")
        participant.add_event_listener(
            MyParticipantEventListener(stt=self.stt, participant=participant)
        )

    def on_participant_left(self, participant: Participant):
        print(f"Participant {participant.display_name} left")
        self.stt.stop(peer_id=participant.id)


class MyParticipantEventListener(ParticipantEventHandler):
    def __init__(self, stt: STT, participant: Participant):
        super().__init__()
        self.stt = stt
        self.participant = participant
        self.dummy_tracks: dict[str, asyncio.Task] = {}
        print(f"Participant-{participant.display_name} :: EventListener initialized")

    async def dummy(self, track):
        try:
            while True:
                await track.recv()
        except Exception as e:
            print("error while consuming dummy stream", e)

    def on_stream_enabled(self, stream: Stream):
        print(
            f"Participant-{self.participant.display_name} :: {stream.kind} stream enabled"
        )
        if stream.kind == "audio":
            self.stt.start(
                peer_id=self.participant.id,
                peer_name=self.participant.display_name,
                stream=stream,
            )
        else:
            # create dummy stream to consume video/screenshare stream to reduce memory usage
            self.dummy_tracks[stream.track.id] = asyncio.create_task(
                self.dummy(track=stream.track)
            )

    def on_stream_disabled(self, stream: Stream):
        print(
            f"Participant-{self.participant.display_name} :: {stream.kind} stream disabled"
        )
        if stream.kind == "audio":
            self.stt.stop(peer_id=self.participant.id)
        else:
            if stream.track.id in self.dummy_tracks:
                self.dummy_tracks[stream.track.id].cancel()
                del self.dummy_tracks[stream.track.id]


