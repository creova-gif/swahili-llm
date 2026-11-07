import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  ArrowDown,
  BookOpen,
  Wheat,
  Scale,
  Smartphone,
  Zap,
  StopCircle,
} from 'lucide-react';
import { ChatMessage, ViewMode, DialectType } from '../types';
import { ChatMessageItem } from './ChatMessage';
import { VoiceInput } from './VoiceInput';

interface ChatStreamProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  viewMode: ViewMode;
  selectedDialect: DialectType;
  onSendMessage: (content: string) => void;
  onStopStreaming?: () => void;
}

const STARTER_PROMPTS = [
  {
    icon: <Scale className="w-4 h-4 text-emerald-400" />,
    title: 'Sheria na Mikataba',
    text: 'Niandikie mkataba wa makubaliano ya biashara ya mazao kwa Kiswahili Sanifu.',
  },
  {
    icon: <Wheat className="w-4 h-4 text-amber-400" />,
    title: 'Kilimo na Masoko',
    text: 'Nieleze mbinu bora za kuhifadhi mahindi baada ya mavuno na bei za soko EAC.',
  },
  {
    icon: <Smartphone className="w-4 h-4 text-cyan-400" />,
    title: 'Ujumuishi wa Kifedha',
    text: 'Jinsi ya kuunganisha mfumo wa M-Pesa Daraja STK Push na kodi za biashara.',
  },
  {
    icon: <BookOpen className="w-4 h-4 text-purple-400" />,
    title: 'Tafsiri ya Lahaja',
    text: 'Nieleze tofauti ya maneno ya Sheng ya Nairobi na Kiswahili Kingwana cha DRC.',
  },
];

export const ChatStream: React.FC<ChatStreamProps> = ({
  messages,
  isStreaming,
  viewMode,
  selectedDialect,
  onSendMessage,
  onStopStreaming,
}) => {
  const [inputText, setInputText] = useState('');
  const [currentlySpeakingId, setCurrentlySpeakingId] = useState<string | null>(null);
  const [showScrollBottom, setShowScrollBottom] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll on new messages or stream chunks
  useEffect(() => {
    if (!showScrollBottom) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, showScrollBottom]);

  // Handle scroll detection
  const handleScroll = () => {
    if (!scrollContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 120;
    setShowScrollBottom(!isNearBottom);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    setShowScrollBottom(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    const text = inputText.trim();
    if (!text || isStreaming) return;
    onSendMessage(text);
    setInputText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  // Swahili Text-to-Speech (TTS) engine
  const handleSpeak = (text: string, messageId: string) => {
    if (!('speechSynthesis' in window)) {
      alert('Kipengele cha sauti (Text-to-Speech) hakitumiki kwenye kivinjari hiki.');
      return;
    }

    if (currentlySpeakingId === messageId) {
      window.speechSynthesis.cancel();
      setCurrentlySpeakingId(null);
      return;
    }

    window.speechSynthesis.cancel();

    // Clean markdown symbols for cleaner TTS speech
    const cleanText = text
      .replace(/<fikiri>[\s\S]*?<\/fikiri>/g, '')
      .replace(/[#*`_~[\]()]/g, '')
      .replace(/https?:\/\/\S+/g, 'kiunganishi cha wavuti');

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    // Pick Swahili voice if available
    const voices = window.speechSynthesis.getVoices();
    const swahiliVoice = voices.find(
      (v) => v.lang.startsWith('sw') || v.lang.includes('sw-') || v.name.toLowerCase().includes('swahili')
    );
    if (swahiliVoice) {
      utterance.voice = swahiliVoice;
    } else {
      utterance.lang = 'sw-TZ';
    }

    utterance.onend = () => {
      setCurrentlySpeakingId(null);
    };

    utterance.onerror = () => {
      setCurrentlySpeakingId(null);
    };

    setCurrentlySpeakingId(messageId);
    window.speechSynthesis.speak(utterance);
  };

  const isWhatsApp = viewMode === 'whatsapp';

  return (
    <div className={`relative flex flex-1 flex-col h-full overflow-hidden ${isWhatsApp ? 'whatsapp-pattern' : 'bg-canvas'}`}>
      {/* Scrollable Message List */}
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto"
      >
        {messages.length === 0 ? (
          /* Empty State / Welcome Hero */
          <div className="flex flex-col items-center justify-center min-h-[80vh] px-4 text-center max-w-2xl mx-auto">
            <div className="relative mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-emerald-600 via-teal-600 to-amber-500 p-0.5 shadow-xl shadow-emerald-950/40">
              <div className="flex h-full w-full items-center justify-center rounded-2xl bg-[#0b101c]">
                <Zap className="h-8 w-8 text-emerald-400 fill-emerald-400" />
              </div>
            </div>

            <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
              Karibu kwenye <span className="text-emerald-400">LughaLLM</span>
            </h2>
            <p className="mt-2 text-xs sm:text-sm text-slate-400 max-w-md">
              Mfumo kiongozi wa Akili Mnemba wenye uelewa wa kina wa Kiswahili Sanifu, Sheng ya Nairobi, na Kingwana cha DRC.
            </p>

            {/* Quick Starters */}
            <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full text-left">
              {STARTER_PROMPTS.map((prompt, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => onSendMessage(prompt.text)}
                  className="group flex flex-col p-3 rounded-xl border border-canvas-border bg-canvas-surface/60 hover:bg-canvas-elevated hover:border-emerald-500/40 transition-all text-left"
                >
                  <div className="flex items-center gap-2 mb-1">
                    {prompt.icon}
                    <span className="text-xs font-semibold text-slate-200 group-hover:text-emerald-300">
                      {prompt.title}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                    "{prompt.text}"
                  </p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="py-4 space-y-1">
            {messages.map((message) => (
              <ChatMessageItem
                key={message.id}
                message={message}
                viewMode={viewMode}
                onSpeak={(text) => handleSpeak(text, message.id)}
                isSpeaking={currentlySpeakingId === message.id}
              />
            ))}
            <div ref={messagesEndRef} className="h-4" />
          </div>
        )}
      </div>

      {/* Floating Scroll to Bottom Button */}
      {showScrollBottom && (
        <button
          onClick={scrollToBottom}
          type="button"
          className="absolute bottom-24 right-6 z-10 flex h-9 w-9 items-center justify-center rounded-full bg-slate-800 text-slate-200 shadow-xl border border-slate-700 hover:bg-slate-700 transition-all"
          title="Shuka chini kabisa"
        >
          <ArrowDown className="h-4 w-4" />
        </button>
      )}

      {/* Input Box Footer */}
      <div className={`p-3 sm:p-4 border-t ${isWhatsApp ? 'bg-[#202c33] border-[#2f3b43]' : 'bg-[#090d16]/95 border-canvas-border'}`}>
        <div className="max-w-4xl mx-auto">
          <div className={`relative flex items-end gap-2 rounded-2xl border p-2 transition-all shadow-lg ${
            isWhatsApp
              ? 'bg-[#2a3942] border-transparent focus-within:border-[#00a884]'
              : 'bg-[#0d1422] border-canvas-border focus-within:border-emerald-500/60 shadow-emerald-950/20'
          }`}>
            {/* Voice Input (Speech-to-Text) */}
            <VoiceInput
              onTranscript={(text) => {
                setInputText((prev) => (prev ? `${prev} ${text}` : text));
              }}
              disabled={isStreaming}
            />

            {/* Multiline Textarea */}
            <textarea
              ref={textareaRef}
              rows={1}
              value={inputText}
              onChange={(e) => {
                setInputText(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = `${Math.min(e.target.scrollHeight, 180)}px`;
              }}
              onKeyDown={handleKeyDown}
              placeholder={
                selectedDialect === 'sheng_nairobi'
                  ? 'Uliza kitu hapa buda... (Enter kutuma)'
                  : selectedDialect === 'kingwana_drc'
                  ? 'Andika ujumbe wako mu Kingwana... (Enter kutuma)'
                  : 'Uliza swali au omba msaada kwa Kiswahili... (Enter kutuma, Shift+Enter kwa mstari mpya)'
              }
              className="flex-1 resize-none bg-transparent py-1.5 px-2 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none min-h-[38px] max-h-[180px]"
            />

            {/* Send or Stop Streaming button */}
            {isStreaming ? (
              <button
                type="button"
                onClick={onStopStreaming}
                className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/20 text-amber-400 hover:bg-amber-500/30 transition-colors"
                title="Sitisha jibu"
              >
                <StopCircle className="h-5 w-5" />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSend}
                disabled={!inputText.trim()}
                className={`flex h-9 w-9 items-center justify-center rounded-xl transition-all ${
                  inputText.trim()
                    ? isWhatsApp
                      ? 'bg-[#00a884] text-white hover:bg-[#029070] active:scale-95'
                      : 'bg-emerald-500 text-white shadow-md shadow-emerald-950/50 hover:bg-emerald-400 active:scale-95'
                    : 'bg-canvas-subtle/50 text-slate-600 cursor-not-allowed'
                }`}
                title="Tuma ujumbe (Enter)"
              >
                <Send className="h-4 w-4" />
              </button>
            )}
          </div>

          <div className="mt-2 flex items-center justify-between px-2 text-[11px] text-slate-500">
            <span className="flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-emerald-400" />
              LughaLLM Sovereign Engine 8B
            </span>
            <span>
              <kbd className="font-mono text-[10px] bg-canvas-elevated px-1 py-0.5 rounded border border-canvas-border">
                Shift + Enter
              </kbd>{' '}
              mstari mpya
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
