import React, { useState, useRef, useEffect } from 'react';
import {
  Sparkles,
  ArrowDown,
  ArrowUp,
  Plus,
  ChevronDown,
  Image as ImageIcon,
  PenLine,
  Code2,
  Globe,
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

export const ChatStream: React.FC<ChatStreamProps> = ({
  messages,
  isStreaming,
  viewMode,
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
    <div className={`relative flex flex-1 flex-col h-full overflow-hidden ${isWhatsApp ? 'whatsapp-pattern' : 'bg-[#111216]'}`}>
      {/* Scrollable Message List */}
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto"
      >
        {messages.length === 0 ? (
          /* ====================================================================
             EMPTY STATE HERO: EXACT EDITORIAL DARK MODE UI/UX DESIGN
             ==================================================================== */
          <div className="flex flex-col items-center justify-center min-h-[82vh] px-4 text-center max-w-3xl mx-auto">
            {/* Elegant Editorial Serif Greeting */}
            <h1 className="font-serif text-3xl sm:text-4xl md:text-5xl text-zinc-100 font-normal tracking-tight mb-8 select-none">
              Good Morning, Mithila
            </h1>

            {/* Centered Floating Input Container */}
            <div className="w-full max-w-xl bg-[#22242c] border border-white/10 rounded-2xl p-3.5 shadow-2xl transition-all focus-within:border-white/20">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="How can I help you today?"
                rows={2}
                className="w-full bg-transparent text-sm text-zinc-100 placeholder-zinc-500 resize-none outline-none leading-relaxed"
              />

              <div className="flex items-center justify-between pt-2 mt-1 border-t border-white/5">
                {/* Left: Attach / Tools */}
                <button
                  type="button"
                  className="h-7 w-7 rounded-full flex items-center justify-center text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
                  title="Ambatisha faili au chombo"
                >
                  <Plus className="w-4 h-4" />
                </button>

                {/* Right Controls: Model Pill, Voice Mic, Send */}
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-white/5 border border-white/5 text-xs text-zinc-300 font-medium cursor-pointer hover:bg-white/10 transition-colors">
                    <span>Quantum 3</span>
                    <ChevronDown className="w-3 h-3 text-zinc-500" />
                  </div>

                  <VoiceInput
                    onTranscript={(t) => setInputText((prev) => (prev ? `${prev} ${t}` : t))}
                    disabled={isStreaming}
                  />

                  <button
                    onClick={handleSend}
                    disabled={!inputText.trim() || isStreaming}
                    type="button"
                    className="h-7 w-7 rounded-full bg-white text-black flex items-center justify-center hover:bg-zinc-200 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                    title="Tuma ujumbe (Enter)"
                  >
                    <ArrowUp className="w-4 h-4 stroke-[2.5]" />
                  </button>
                </div>
              </div>
            </div>

            {/* Quick Action Suggestion Chips (from sample UI) */}
            <div className="mt-5 flex flex-wrap items-center justify-center gap-2 max-w-xl">
              <button
                type="button"
                onClick={() => onSendMessage('Tengeneza picha au mchoro wenye mandhari ya asili ya Afrika Mashariki.')}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#1b1c22] border border-white/5 text-xs text-zinc-300 hover:bg-[#252832] hover:border-white/15 transition-all shadow-sm"
              >
                <ImageIcon className="w-3.5 h-3.5 text-zinc-400" />
                <span>Create an image</span>
              </button>

              <button
                type="button"
                onClick={() => onSendMessage('Niandikie hotuba rasmi au barua ya kikazi yenye ufasaha wa Kiswahili Sanifu.')}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#1b1c22] border border-white/5 text-xs text-zinc-300 hover:bg-[#252832] hover:border-white/15 transition-all shadow-sm"
              >
                <PenLine className="w-3.5 h-3.5 text-zinc-400" />
                <span>Smart Writing</span>
              </button>

              <button
                type="button"
                onClick={() => onSendMessage('Nisaidie kuandika kodi safi ya Python na FastAPI kuunganisha Safaricom M-Pesa API.')}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#1b1c22] border border-white/5 text-xs text-zinc-300 hover:bg-[#252832] hover:border-white/15 transition-all shadow-sm"
              >
                <Code2 className="w-3.5 h-3.5 text-zinc-400" />
                <span>AI Coding</span>
              </button>

              <button
                type="button"
                onClick={() => onSendMessage('Fanya utafiti wa kina wa athari za kilimo na mabadiliko ya tabianchi kanda ya Afrika Mashariki.')}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#1b1c22] border border-white/5 text-xs text-zinc-300 hover:bg-[#252832] hover:border-white/15 transition-all shadow-sm"
              >
                <Globe className="w-3.5 h-3.5 text-zinc-400" />
                <span>Deep Research</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="py-6 max-w-3xl mx-auto px-4 space-y-4">
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
          className="absolute bottom-28 right-8 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-zinc-800 text-zinc-200 shadow-xl border border-white/10 hover:bg-zinc-700 transition-all"
          title="Shuka chini kabisa"
        >
          <ArrowDown className="h-4 w-4" />
        </button>
      )}

      {/* Floating Bottom Input Bar (when conversation is active) */}
      {messages.length > 0 && (
        <div className="p-4 pt-1 bg-gradient-to-t from-[#111216] via-[#111216]/90 to-transparent">
          <div className="max-w-2xl mx-auto">
            <div className="bg-[#22242c] border border-white/10 rounded-2xl p-3 shadow-2xl transition-all focus-within:border-white/20">
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
                placeholder="How can I help you today?"
                className="w-full bg-transparent text-sm text-zinc-100 placeholder-zinc-500 resize-none outline-none leading-relaxed min-h-[36px] max-h-[180px]"
              />

              <div className="flex items-center justify-between pt-2 mt-1 border-t border-white/5">
                <button
                  type="button"
                  className="h-7 w-7 rounded-full flex items-center justify-center text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
                  title="Ambatisha faili au chombo"
                >
                  <Plus className="w-4 h-4" />
                </button>

                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-white/5 border border-white/5 text-xs text-zinc-300 font-medium cursor-pointer hover:bg-white/10 transition-colors">
                    <span>Quantum 3</span>
                    <ChevronDown className="w-3 h-3 text-zinc-500" />
                  </div>

                  <VoiceInput
                    onTranscript={(t) => setInputText((prev) => (prev ? `${prev} ${t}` : t))}
                    disabled={isStreaming}
                  />

                  {isStreaming ? (
                    <button
                      type="button"
                      onClick={onStopStreaming}
                      className="h-7 w-7 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center hover:bg-amber-500/30 transition-colors"
                      title="Sitisha jibu"
                    >
                      <StopCircle className="h-4 w-4" />
                    </button>
                  ) : (
                    <button
                      onClick={handleSend}
                      disabled={!inputText.trim()}
                      type="button"
                      className="h-7 w-7 rounded-full bg-white text-black flex items-center justify-center hover:bg-zinc-200 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                      title="Tuma ujumbe (Enter)"
                    >
                      <ArrowUp className="w-4 h-4 stroke-[2.5]" />
                    </button>
                  )}
                </div>
              </div>
            </div>

            <div className="mt-1.5 flex items-center justify-between px-2 text-[10px] text-zinc-500">
              <span className="flex items-center gap-1">
                <Sparkles className="w-2.5 h-2.5 text-emerald-400" />
                LughaLLM Sovereign Engine 8B
              </span>
              <span>
                <kbd className="font-mono bg-white/5 px-1 py-0.5 rounded border border-white/5">
                  Shift + Enter
                </kbd>{' '}
                kwa mstari mpya
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
