export interface Message {
  participantId: string;
  text: string;
  timestamp: number;
  isAI: boolean;
}

export interface MeetingControlsProps {
  onClose: () => void;
}

export interface ChatPanelProps {
  messages: Message[];
  isAIConnected: boolean;
  meetingId: string;
}
