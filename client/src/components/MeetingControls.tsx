import React from "react";
import { X } from "lucide-react";
import { MeetingControlsProps } from "../types/meeting";

export const MeetingControls: React.FC<MeetingControlsProps> = ({
  onClose,
}) => {
  return (
    <div className="absolute top-4 right-4 z-50">
      <button
        onClick={onClose}
        className="p-2 rounded-full bg-sky-500 hover:bg-sky-600 transition-colors"
        aria-label="End meeting"
      >
        <X className="w-5 h-5 text-white" />
      </button>
    </div>
  );
};
