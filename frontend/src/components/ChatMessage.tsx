import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Copy,
  Check,
  Volume2,
  Square,
  Bot,
  User,
  CheckCheck,
} from 'lucide-react';
import { ChatMessage as ChatMessageType, ViewMode } from '../types';
import { ThinkingDrawer } from './ThinkingDrawer';

interface ChatMessageProps {
  message: ChatMessageType;
  viewMode: ViewMode;
  onSpeak?: (text: string) => void;
  isSpeaking?: boolean;
}

// Code Block with Copy-to-Clipboard
const CodeBlock: React.FC<{ language?: string; value: string }> = ({ language, value }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative my-3 overflow-hidden rounded-lg border border-slate-700/60 bg-[#090e17] font-mono text-xs shadow-md">
      <div className="flex items-center justify-between border-b border-slate-800 bg-[#0d1522] px-3.5 py-1.5 text-slate-400">
        <span className="font-semibold text-[11px] uppercase tracking-wider text-emerald-400/90">
          {language || 'code'}
        </span>
        <button
          onClick={handleCopy}
          type="button"
          className="flex items-center gap-1 rounded px-2 py-0.5 text-[11px] text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
          title="Nakili msimbo"
        >
          {copied ? (
            <>
              <Check className="h-3 w-3 text-emerald-400" />
              <span className="text-emerald-400">Imenakiliwa!</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span>Nakili</span>
            </>
          )}
        </button>
      </div>
      <div className="overflow-x-auto p-3 text-slate-200 leading-relaxed">
        <pre>
          <code>{value}</code>
        </pre>
      </div>
    </div>
  );
};

export const ChatMessageItem: React.FC<ChatMessageProps> = ({
  message,
  viewMode,
  onSpeak,
  isSpeaking = false,
}) => {
  const [copiedMessage, setCopiedMessage] = useState(false);
  const isUser = message.role === 'user';

  const copyMessageText = () => {
    navigator.clipboard.writeText(message.content);
    setCopiedMessage(true);
    setTimeout(() => setCopiedMessage(false), 2000);
  };

  // WhatsApp View Simulator Mode
  if (viewMode === 'whatsapp') {
    return (
      <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} my-1.5 px-3`}>
        <div
          className={`relative max-w-[85%] sm:max-w-[75%] rounded-lg px-3 py-2 text-sm shadow-sm ${
            isUser
              ? 'bg-[#005c4b] text-[#e9edef] rounded-tr-none'
              : 'bg-[#202c33] text-[#d1d7db] rounded-tl-none'
          }`}
        >
          {/* System-2 Thinking in WhatsApp View */}
          {!isUser && message.thinkingContent && (
            <ThinkingDrawer
              content={message.thinkingContent}
              isStreaming={message.isStreaming}
              tokensCount={message.reasoningTokens}
              isWhatsAppView={true}
            />
          )}

          {/* Message Content */}
          <div className="whatsapp-message-body break-words prose-custom leading-relaxed">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  const codeString = String(children).replace(/\n$/, '');
                  return match ? (
                    <CodeBlock language={match[1]} value={codeString} />
                  ) : (
                    <code className="bg-black/30 px-1 py-0.5 rounded text-emerald-300 font-mono text-xs" {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>

          {/* WhatsApp Footer: Time, Audio Playback, and Double Checkmarks */}
          <div className="mt-1 flex items-center justify-end gap-1.5 text-[10px] text-[#8696a0]">
            {!isUser && onSpeak && (
              <button
                onClick={() => onSpeak(message.content)}
                type="button"
                className="hover:text-emerald-400 mr-1 flex items-center gap-1"
                title="Sikiliza sauti"
              >
                {isSpeaking ? (
                  <Square className="w-3 h-3 text-amber-400 fill-amber-400 animate-pulse" />
                ) : (
                  <Volume2 className="w-3 h-3" />
                )}
              </button>
            )}
            <span>{message.timestamp}</span>
            {isUser && <CheckCheck className="h-3.5 w-3.5 text-[#53bdeb]" />}
          </div>
        </div>
      </div>
    );
  }

  // Enterprise Modern Dark Mode
  return (
    <div
      className={`group relative flex w-full gap-3 py-4 px-4 sm:px-6 transition-colors ${
        isUser ? 'bg-transparent' : 'bg-canvas-surface/60 border-y border-canvas-border'
      }`}
    >
      {/* Avatar */}
      <div className="flex-shrink-0 pt-0.5">
        {isUser ? (
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-800 text-slate-300 border border-slate-700 shadow-sm">
            <User className="h-4 w-4" />
          </div>
        ) : (
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-600 to-teal-800 text-white shadow-md shadow-emerald-950/40 border border-emerald-500/30">
            <Bot className="h-4 w-4" />
          </div>
        )}
      </div>

      {/* Main Body */}
      <div className="flex-1 min-w-0 overflow-hidden">
        {/* Header line */}
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold tracking-wide text-slate-200">
              {isUser ? 'Wewe' : 'LughaLLM Sovereign Swahili'}
            </span>
            {message.detectedDialect && !isUser && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                {message.detectedDialect.replace('_', ' ')}
              </span>
            )}
            <span className="text-[11px] text-slate-500">{message.timestamp}</span>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {!isUser && onSpeak && (
              <button
                onClick={() => onSpeak(message.content)}
                type="button"
                className="flex items-center gap-1 rounded px-2 py-1 text-xs text-slate-400 hover:bg-canvas-elevated hover:text-emerald-400 transition-colors"
                title="Sikiliza kwa Sauti (Swahili TTS)"
              >
                {isSpeaking ? (
                  <>
                    <Square className="h-3 w-3 text-amber-400 fill-amber-400" />
                    <span className="text-amber-400 font-mono text-[11px]">Simamisha</span>
                  </>
                ) : (
                  <>
                    <Volume2 className="h-3 w-3" />
                    <span className="font-mono text-[11px]">Sikiliza Sauti</span>
                  </>
                )}
              </button>
            )}

            <button
              onClick={copyMessageText}
              type="button"
              className="rounded p-1 text-slate-400 hover:bg-canvas-elevated hover:text-slate-200 transition-colors"
              title="Nakili ujumbe"
            >
              {copiedMessage ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            </button>
          </div>
        </div>

        {/* Collapsible <fikiri> System-2 Deep Reasoning Drawer */}
        {!isUser && message.thinkingContent && (
          <ThinkingDrawer
            content={message.thinkingContent}
            isStreaming={message.isStreaming}
            tokensCount={message.reasoningTokens}
            durationMs={message.thinkingDurationMs}
            isWhatsAppView={false}
          />
        )}

        {/* Markdown Content */}
        <div className="prose-custom text-slate-200 text-[13.5px] leading-relaxed break-words">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                const codeString = String(children).replace(/\n$/, '');
                return match ? (
                  <CodeBlock language={match[1]} value={codeString} />
                ) : (
                  <code
                    className="rounded bg-slate-800/80 px-1.5 py-0.5 font-mono text-xs text-emerald-300 border border-slate-700/50"
                    {...props}
                  >
                    {children}
                  </code>
                );
              },
            }}
          >
            {message.content}
          </ReactMarkdown>

          {message.isStreaming && (
            <span className="inline-block w-2 h-4 ml-1 bg-emerald-400 animate-pulse align-middle" />
          )}
        </div>
      </div>
    </div>
  );
};
