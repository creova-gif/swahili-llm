import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff } from 'lucide-react';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

// Declare SpeechRecognition interfaces for TypeScript
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export const VoiceInput: React.FC<VoiceInputProps> = ({ onTranscript, disabled = false }) => {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setIsSupported(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      // Prefer Swahili (Tanzania / Kenya)
      recognition.lang = 'sw-TZ';

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }

        const transcript = finalTranscript || interimTranscript;
        if (transcript) {
          onTranscript(transcript);
        }
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    } catch (err) {
      console.warn('SpeechRecognition initialization failed:', err);
      setIsSupported(false);
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // ignore
        }
      }
    };
  }, [onTranscript]);

  const toggleListening = () => {
    if (!isSupported) {
      alert('Kipengele cha kutambua sauti (Speech-to-Text) hakipatikani kwenye kivinjari hiki. Tafadhali tumia Google Chrome au Microsoft Edge.');
      return;
    }

    if (isListening) {
      try {
        recognitionRef.current?.stop();
      } catch {
        // ignore
      }
      setIsListening(false);
    } else {
      try {
        recognitionRef.current?.start();
        setIsListening(true);
      } catch (err) {
        console.warn('Could not start speech recognition:', err);
        setIsListening(false);
      }
    }
  };

  return (
    <button
      type="button"
      onClick={toggleListening}
      disabled={disabled}
      title={
        !isSupported
          ? 'Sauti (STT) haipatikani'
          : isListening
          ? 'Acha kusikiliza (Bonyeza kumaliza)'
          : 'Ongea kwa Kiswahili (Sauti-hadi-Maandishi)'
      }
      className={`relative inline-flex items-center justify-center p-2 rounded-lg transition-all ${
        isListening
          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/50 shadow-lg shadow-rose-500/20'
          : 'bg-canvas-subtle/80 text-slate-400 hover:text-slate-200 hover:bg-canvas-elevated border border-canvas-border'
      } disabled:opacity-50 disabled:cursor-not-allowed`}
    >
      {isListening ? (
        <>
          <span className="absolute inset-0 rounded-lg animate-ping bg-rose-500/20 pointer-events-none"></span>
          <MicOff className="w-4 h-4 text-rose-400 relative z-10" />
        </>
      ) : (
        <Mic className="w-4 h-4" />
      )}
    </button>
  );
};
