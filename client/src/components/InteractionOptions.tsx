import React from 'react';
import { Mic, Video, Loader2 } from 'lucide-react';

interface InteractionOptionsProps {
  onStart: (useVideo: boolean) => void;
  isLoading: boolean;
}

export const InteractionOptions: React.FC<InteractionOptionsProps> = ({ 
  onStart,
  isLoading 
}) => {
  return (
    <div className="flex flex-col sm:flex-row gap-6 justify-center">
      <button
        onClick={() => onStart(false)}
        disabled={isLoading}
        className="group relative flex flex-col items-center p-8 bg-gray-800/50 hover:bg-gray-800 rounded-2xl transition-all duration-200 transform hover:-translate-y-1"
      >
        <div className="absolute inset-0 bg-blue-500/5 rounded-2xl group-hover:bg-blue-500/10 transition-colors" />
        <div className="p-4 rounded-full bg-blue-500/10 mb-4 group-hover:bg-blue-500/20 transition-colors">
          <Mic className="w-8 h-8 text-blue-400" />
        </div>
        <span className="text-white font-medium text-lg mb-2">Audio Chat</span>
        <span className="text-gray-400 text-sm">Talk with voice only</span>
      </button>
      
      <button
        onClick={() => onStart(true)}
        disabled={isLoading}
        className="group relative flex flex-col items-center p-8 bg-gray-800/50 hover:bg-gray-800 rounded-2xl transition-all duration-200 transform hover:-translate-y-1"
      >
        <div className="absolute inset-0 bg-blue-500/5 rounded-2xl group-hover:bg-blue-500/10 transition-colors" />
        <div className="p-4 rounded-full bg-blue-500/10 mb-4 group-hover:bg-blue-500/20 transition-colors">
          <Video className="w-8 h-8 text-blue-400" />
        </div>
        <span className="text-white font-medium text-lg mb-2">Video Chat</span>
        <span className="text-gray-400 text-sm">Face-to-face interaction</span>
      </button>

      {isLoading && (
        <div className="absolute inset-0 bg-gray-900/50 flex items-center justify-center backdrop-blur-sm">
          <div className="flex items-center space-x-3">
            <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
            <span className="text-white">Initializing...</span>
          </div>
        </div>
      )}
    </div>
  );
};