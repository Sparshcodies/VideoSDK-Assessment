import React from "react";
import { useMeeting, usePubSub } from "@videosdk.live/react-sdk";
import { MeetingControls } from "./MeetingControls";
import { ChatPanel } from "./ChatPanel";
import { Message } from "../types/meeting";
import { Loader2 } from "lucide-react";
import { ParticipantCard } from "./ParticipantCard";

interface MeetingPopupProps {
  onClose: () => void;
  meetingId: string;
}

export const MeetingPopup: React.FC<MeetingPopupProps> = ({
  onClose,
  meetingId,
}) => {
  const { end, participants, localParticipant } = useMeeting({
    onMeetingJoined: () => {
      setIsInitializing(false);
    },
  });
  const [messages, setMessages] = React.useState<Message[]>([]);
  const [isInitializing, setIsInitializing] = React.useState(true);

  const {} = usePubSub("CHAT", {
    onMessageReceived: ({ senderId, message }) => {
      const newMessage: Message = {
        participantId: senderId,
        text: message,
        timestamp: Date.now(),
        isAI:
          senderId !==
          (participants.get(participants.keys().next().value || "")?.id || ""),
      };
      setMessages((prev) => [...prev, newMessage]);
    },
  });
  console.log(participants);

  const handleClose = () => {
    end();
    onClose();
  };

  const isAIConnected = participants.size > 1;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} />
      <div
        className="relative w-[80vw] h-[90vh] bg-gray-900 rounded-xl shadow-2xl overflow-hidden transform transition-all"
        style={{ animation: "zoomIn 0.3s ease-out" }}
      >
        {isInitializing ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center space-y-4">
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto" />
              <p className="text-white text-lg">
                Conversation will start shortly...
              </p>
            </div>
          </div>
        ) : (
          <div className="flex h-full">
            <div className="flex-1 relative p-6">
              <div className="flex flex-col space-y-4 h-full">
                {/* Human Participant Card */}
                {localParticipant && (
                  <ParticipantCard
                    isLocal
                    name="You"
                    participant={localParticipant}
                  />
                )}

                {/* AI Copilot Card */}
                {participants.size > 1 && (
                  <ParticipantCard
                    isAI
                    name="Bucky"
                    participant={[...participants.values()][1]}
                    isConnected={isAIConnected}
                  />
                )}
              </div>

              <MeetingControls onClose={handleClose} />
            </div>

            <ChatPanel
              messages={messages}
              isAIConnected={isAIConnected}
              meetingId={meetingId}
            />
          </div>
        )}
      </div>
    </div>
  );
};
