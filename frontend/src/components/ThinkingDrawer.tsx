import React, { useState } from 'react';
import { BrainCircuit, ChevronDown, ChevronUp, Sparkles, CheckCircle2 } from 'lucide-react';

interface ThinkingDrawerProps {
  content: string;
  isStreaming?: boolean;
  tokensCount?: number;
  durationMs?: number;
  isWhatsAppView?: boolean;
}

export const ThinkingDrawer: React.FC<ThinkingDrawerProps> = ({
  content,
  isStreaming = false,
  tokensCount,
  durationMs,
  isWhatsAppView = false,
}) => {
  const [isOpen, setIsOpen] = useState(true);

  if (!content) return null;

  // Approximate token calculation if not explicitly provided
  const tokens = tokensCount || Math.max(1, Math.round(content.split(/\s+/).length * 1.3));

  if (isWhatsAppView) {
    return (
      <div className="mb-2 text-xs rounded border border-emerald-800/40 bg-[#122e26]/60 p-2 text-emerald-300">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex w-full items-center justify-between text-left font-mono font-medium hover:text-emerald-200 transition-colors"
          type="button"
        >
          <div className="flex items-center gap-1.5">
            <BrainCircuit className="w-3.5 h-3.5 text-emerald-400" />
            <span>&lt;fikiri&gt; System-2 Reasoning</span>
            <span className="text-[10px] text-emerald-400/80 bg-emerald-950/60 px-1.5 py-0.5 rounded">
              {tokens} tokens
            </span>
          </div>
          {isOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
        {isOpen && (
          <div className="mt-2 whitespace-pre-wrap font-mono text-[11px] leading-relaxed text-emerald-200/90 border-t border-emerald-800/30 pt-2 max-h-48 overflow-y-auto">
            {content}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="mb-3 rounded-lg border border-amber-500/25 bg-amber-950/20 shadow-sm backdrop-blur-sm transition-all overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center justify-between px-3.5 py-2.5 text-left text-xs text-amber-300/90 hover:bg-amber-900/20 transition-colors"
        type="button"
      >
        <div className="flex items-center gap-2">
          <div className="relative flex items-center justify-center">
            <BrainCircuit className="w-4 h-4 text-amber-400" />
            {isStreaming && (
              <span className="absolute -top-0.5 -right-0.5 flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
              </span>
            )}
          </div>
          <span className="font-medium tracking-wide flex items-center gap-1.5">
            <span>Mchakato wa Kufikiri Kina</span>
            <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
              System-2
            </span>
          </span>

          <span className="text-[11px] font-mono text-amber-300/70 ml-1">
            ({tokens} tokens{durationMs ? ` • ${(durationMs / 1000).toFixed(1)}s` : ''})
          </span>
        </div>

        <div className="flex items-center gap-2">
          {isStreaming ? (
            <span className="flex items-center gap-1 text-[11px] text-amber-400 animate-pulse font-mono">
              <Sparkles className="w-3 h-3" />
              Inachambua...
            </span>
          ) : (
            <span className="flex items-center gap-1 text-[11px] text-emerald-400/90 font-mono">
              <CheckCircle2 className="w-3 h-3" />
              Tayari
            </span>
          )}
          {isOpen ? (
            <ChevronUp className="w-4 h-4 text-amber-400/80" />
          ) : (
            <ChevronDown className="w-4 h-4 text-amber-400/80" />
          )}
        </div>
      </button>

      {isOpen && (
        <div className="border-t border-amber-500/15 bg-black/30 px-3.5 py-3 text-xs font-mono text-amber-200/80 leading-relaxed max-h-64 overflow-y-auto whitespace-pre-wrap selection:bg-amber-500/30">
          {content}
        </div>
      )}
    </div>
  );
};
