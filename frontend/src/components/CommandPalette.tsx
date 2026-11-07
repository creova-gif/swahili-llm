import React, { useState, useEffect, useRef } from 'react';
import {
  Search,
  MessageSquarePlus,
  Coins,
  Globe,
  BrainCircuit,
  Smartphone,
  Trash2,
  Zap,
} from 'lucide-react';
import { DialectType } from '../types';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onNewChat: () => void;
  onOpenBilling: () => void;
  onSelectDialect: (d: DialectType) => void;
  onToggleWhatsApp: () => void;
  onToggleThinking: () => void;
  onClearChat: () => void;
  isWhatsApp: boolean;
  includeThinking: boolean;
  currentDialect: DialectType;
}

interface CommandAction {
  id: string;
  label: string;
  shortcut?: string;
  icon: React.ReactNode;
  category: string;
  action: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  onNewChat,
  onOpenBilling,
  onSelectDialect,
  onToggleWhatsApp,
  onToggleThinking,
  onClearChat,
  isWhatsApp,
  includeThinking,
}) => {
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setSearch('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  const actions: CommandAction[] = [
    {
      id: 'new_chat',
      label: '+ Anzisha Mazungumzo Mapya',
      shortcut: 'Cmd+O',
      icon: <MessageSquarePlus className="w-4 h-4 text-emerald-400" />,
      category: 'Mazungumzo',
      action: () => {
        onNewChat();
        onClose();
      },
    },
    {
      id: 'billing',
      label: 'Ongeza Salio la Token (M-Pesa)',
      shortcut: 'Cmd+B',
      icon: <Coins className="w-4 h-4 text-amber-400" />,
      category: 'Akaunti',
      action: () => {
        onOpenBilling();
        onClose();
      },
    },
    {
      id: 'toggle_whatsapp',
      label: isWhatsApp ? 'Rejea Kwenye Mwonekano wa Kawaida (Enterprise)' : 'Badili kwenda WhatsApp Simulator (2G View)',
      shortcut: 'Cmd+W',
      icon: <Smartphone className="w-4 h-4 text-[#00a884]" />,
      category: 'Mwonekano',
      action: () => {
        onToggleWhatsApp();
        onClose();
      },
    },
    {
      id: 'toggle_thinking',
      label: includeThinking ? 'Zima <fikiri> System-2 Deep Reasoning' : 'Washa <fikiri> System-2 Deep Reasoning',
      shortcut: 'Cmd+T',
      icon: <BrainCircuit className="w-4 h-4 text-cyan-400" />,
      category: 'Inference',
      action: () => {
        onToggleThinking();
        onClose();
      },
    },
    {
      id: 'clear_chat',
      label: 'Futa Ujumbe wa Mazungumzo Haya',
      icon: <Trash2 className="w-4 h-4 text-rose-400" />,
      category: 'Mazungumzo',
      action: () => {
        onClearChat();
        onClose();
      },
    },
    {
      id: 'dialect_sanifu',
      label: 'Lahaja: Kiswahili Sanifu (Tanzania / Kenya Rasmi)',
      icon: <Globe className="w-4 h-4 text-slate-300" />,
      category: 'Lahaja za Kiswahili',
      action: () => {
        onSelectDialect('kiswahili_sanifu');
        onClose();
      },
    },
    {
      id: 'dialect_sheng',
      label: 'Lahaja: Nairobi Sheng (Mtaa Slang)',
      icon: <Globe className="w-4 h-4 text-amber-400" />,
      category: 'Lahaja za Kiswahili',
      action: () => {
        onSelectDialect('sheng_nairobi');
        onClose();
      },
    },
    {
      id: 'dialect_kingwana',
      label: 'Lahaja: DRC Kingwana (Congo Mashariki)',
      icon: <Globe className="w-4 h-4 text-cyan-400" />,
      category: 'Lahaja za Kiswahili',
      action: () => {
        onSelectDialect('kingwana_drc');
        onClose();
      },
    },
    {
      id: 'dialect_uganda',
      label: 'Lahaja: Uganda Trade Swahili',
      icon: <Globe className="w-4 h-4 text-emerald-400" />,
      category: 'Lahaja za Kiswahili',
      action: () => {
        onSelectDialect('swahili_uganda');
        onClose();
      },
    },
    {
      id: 'dialect_auto',
      label: 'Lahaja: Otomatiki (Utambuzi wa Moja kwa Moja)',
      icon: <Zap className="w-4 h-4 text-purple-400" />,
      category: 'Lahaja za Kiswahili',
      action: () => {
        onSelectDialect('auto');
        onClose();
      },
    },
  ];

  const filtered = actions.filter(
    (a) =>
      a.label.toLowerCase().includes(search.toLowerCase()) ||
      a.category.toLowerCase().includes(search.toLowerCase())
  );

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % (filtered.length || 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + filtered.length) % (filtered.length || 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filtered[selectedIndex]) {
        filtered[selectedIndex].action();
      }
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-24 p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div
        className="w-full max-w-xl rounded-xl border border-canvas-border bg-[#0d1424] shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
      >
        <div className="flex items-center border-b border-canvas-border px-4 py-3">
          <Search className="h-4 w-4 text-slate-400 mr-2.5 flex-shrink-0" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Andika amri au tafuta vitendo... (Cmd+K)"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setSelectedIndex(0);
            }}
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          <kbd className="hidden sm:inline-block rounded bg-canvas-elevated px-2 py-0.5 text-[10px] font-mono text-slate-400 border border-canvas-border">
            ESC
          </kbd>
        </div>

        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <div className="py-6 text-center text-xs text-slate-500">
              Hakuna amri inayolingana na utafutaji wako.
            </div>
          ) : (
            filtered.map((item, idx) => {
              const isSelected = idx === selectedIndex;
              return (
                <button
                  key={item.id}
                  onClick={item.action}
                  type="button"
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-xs text-left transition-colors ${
                    isSelected
                      ? 'bg-emerald-500/15 text-emerald-200 border border-emerald-500/30'
                      : 'text-slate-300 hover:bg-canvas-elevated border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    {item.icon}
                    <span>{item.label}</span>
                  </div>
                  {item.shortcut && (
                    <kbd className="rounded bg-black/40 px-1.5 py-0.5 text-[10px] font-mono text-slate-400 border border-slate-800">
                      {item.shortcut}
                    </kbd>
                  )}
                </button>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
