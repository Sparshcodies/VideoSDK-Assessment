import React from "react";
import { useParticipant } from "@videosdk.live/react-sdk";
import { Bot, User, Mic } from "lucide-react";

interface ParticipantCardProps {
  isLocal?: boolean;
  isAI?: boolean;
  name: string;
  participant?: any;
  isConnected?: boolean;
}

export const ParticipantCard: React.FC<ParticipantCardProps> = ({
  isLocal,
  isAI,
  name,
  participant,
  isConnected = true,
}) => {
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const audioRef = React.useRef<HTMLAudioElement>(null);
  console.log(participant);
  const { webcamStream, micStream, webcamOn, micOn } = useParticipant(
    participant.id
  );

  // Handle video stream
  React.useEffect(() => {
    if (videoRef.current && webcamStream && webcamOn) {
      const mediaStream = new MediaStream();
      mediaStream.addTrack(webcamStream.track);
      videoRef.current.srcObject = mediaStream;
      videoRef.current
        .play()
        .catch((error) =>
          console.error("audioRef.current.play() failed", error)
        );
    }
  }, [webcamStream, webcamOn, videoRef.current]);

  // Handle audio stream
  React.useEffect(() => {
    if (audioRef.current && micStream && micOn) {
      const mediaStream = new MediaStream();
      mediaStream.addTrack(micStream.track);
      audioRef.current.srcObject = mediaStream;

      audioRef.current
        .play()
        .catch((error) =>
          console.error("audioRef.current.play() failed", error)
        );
    }
  }, [micStream, micOn]);

  return (
    <div className="relative rounded-2xl overflow-hidden bg-gray-800 h-[calc(50%-0.5rem)]">
      {/* Video Container */}
      <div className="absolute inset-0">
        {webcamOn && webcamStream ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted={isLocal}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="p-4 rounded-full bg-gray-700">
              {isAI ? (
                <Bot className="w-8 h-8 text-blue-400" />
              ) : (
                <User className="w-8 h-8 text-blue-400" />
              )}
            </div>
          </div>
        )}
      </div>

      {/* Audio Element */}
      <audio ref={audioRef} autoPlay playsInline muted={isLocal} />

      {/* Overlay for when participant is not connected */}
      {!isConnected && (
        <div className="absolute inset-0 bg-gray-900/90 flex items-center justify-center">
          <div className="text-center space-y-4">
            <Bot className="w-12 h-12 text-blue-500 animate-pulse mx-auto" />
            <p className="text-white text-lg">
              Waiting for AI Copilot to join...
            </p>
          </div>
        </div>
      )}

      {/* Participant Info */}
      <div className="absolute top-4 left-4 flex items-center space-x-2">
        <div className="p-2 rounded-full bg-blue-500/20">
          {isAI ? (
            <Bot className="w-5 h-5 text-blue-400" />
          ) : (
            <User className="w-5 h-5 text-blue-400" />
          )}
        </div>
        <span className="text-white font-medium">{name}</span>
      </div>

      {/* Audio Indicator */}
      {micOn && (
        <div className="absolute bottom-4 left-4 flex items-center space-x-2">
          <div className="p-2 rounded-full bg-green-500/20">
            <Mic className="w-4 h-4 text-green-400" />
          </div>
          <span className="text-sm text-green-400">Speaking</span>
        </div>
      )}
    </div>
  );
};
