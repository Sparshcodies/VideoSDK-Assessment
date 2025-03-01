import React, { useState } from "react";
import { MessageSquare, Clipboard, Check } from "lucide-react";
import { ChatPanelProps } from "../types/meeting";

export const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  isAIConnected,
  meetingId,
}) => {
  const chatRef = React.useRef<HTMLDivElement>(null);
  const [copied, setCopied] = useState(false); // State to track copy action

  // Function to copy Meeting ID
  const copyMeetingId = () => {
    if (meetingId) {
      navigator.clipboard.writeText(meetingId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000); // Reset after 2s
    }
  };

  React.useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="w-80 bg-gray-900 border-l border-gray-700 h-full flex flex-col">
      {/* Chat Panel Header */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white">Conversation</h2>
      </div>

      {/* Meeting ID Display */}
      <div className="p-4 border-b border-gray-700 flex items-center justify-between">
        <span className="text-gray-300 text-sm">
          Meeting ID: {meetingId || "Loading..."}
        </span>
        <button
          onClick={copyMeetingId}
          className="text-blue-400 hover:text-blue-300 flex items-center space-x-1"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-400" />
          ) : (
            <Clipboard className="w-4 h-4" />
          )}
          <span>{copied ? "Copied" : "Copy"}</span>
        </button>
      </div>

      {/* Chat Panel Content */}
      {!isAIConnected ? (
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center space-y-4">
            <MessageSquare className="w-12 h-12 text-gray-600 mx-auto" />
            <p className="text-gray-400">
              Chat will start once the AI Copilot joins.
            </p>
          </div>
        </div>
      ) : (
        <div ref={chatRef} className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <p className="text-gray-400 text-center">
              Conversation hasn't started yet.
            </p>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg ${
                  message.isAI ? "bg-blue-900/30 ml-4" : "bg-gray-800 mr-4"
                }`}
              >
                <p className="text-xs text-gray-400 mb-1">
                  {message.isAI ? "AI Copilot" : "You"}
                </p>
                <p className="text-white">{message.text}</p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
