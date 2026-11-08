import React, { useState } from 'react';
import {
  Menu,
  Coins,
  BrainCircuit,
  Smartphone,
  Command,
  ChevronDown,
  Check,
} from 'lucide-react';
import { DialectType, DialectOption, KeyBalanceInfo, ViewMode } from '../types';

interface HeaderProps {
  onToggleSidebar: () => void;
  selectedDialect: DialectType;
  onSelectDialect: (d: DialectType) => void;
  includeThinking: boolean;
  onToggleThinking: () => void;
  viewMode: ViewMode;
  onToggleViewMode: () => void;
  balanceInfo: KeyBalanceInfo | null;
  onOpenBilling: () => void;
  onOpenCommandPalette: () => void;
}

export const DIALECT_OPTIONS: DialectOption[] = [
  {
    id: 'auto',
    label: 'Otomatiki (Utambuzi)',
    region: 'Afrika Mashariki',
    flag: '⚡',
    sample: 'Inatambua lahaja yoyote kiotomatiki',
    tagline: 'Auto-detection',
  },
  {
    id: 'kiswahili_sanifu',
    label: 'Kiswahili Sanifu',
    region: 'Tanzania & Kenya',
    flag: '🇹🇿',
    sample: 'Habari za asubuhi, naweza kukusaidiaje leo?',
    tagline: 'Official Standard Swahili',
  },
  {
    id: 'sheng_nairobi',
    label: 'Nairobi Sheng',
    region: 'Kenya (Nairobi)',
    flag: '🇰🇪',
    sample: 'Niaje buda! Rada yako ikoje leo?',
    tagline: 'Urban Youth Slang',
  },
  {
    id: 'kingwana_drc',
    label: 'DRC Kingwana',
    region: 'Congo Mashariki',
    flag: '🇨🇩',
    sample: 'Mbote ndeko! Habari ya kazi mu kanda yetu?',
    tagline: 'Eastern Congo Trade Swahili',
  },
  {
    id: 'swahili_uganda',
    label: 'Uganda Trade Swahili',
    region: 'Uganda / Kampala',
    flag: '🇺🇬',
    sample: 'Oli otya! Mazungumzo ya biashara na mabadilishano.',
    tagline: 'Great Lakes Commercial Swahili',
  },
  {
    id: 'coastal_swahili',
    label: 'Coastal Swahili (Kiunguja)',
    region: 'Mombasa / Zanzibar',
    flag: '🏝️',
    sample: 'Sabalkheri mheshimiwa, shikamoo!',
    tagline: 'Traditional Island & Coastal Dialect',
  },
];

export const Header: React.FC<HeaderProps> = ({
  onToggleSidebar,
  selectedDialect,
  onSelectDialect,
  includeThinking,
  onToggleThinking,
  viewMode,
  onToggleViewMode,
  balanceInfo,
  onOpenBilling,
  onOpenCommandPalette,
}) => {
  const [isDialectDropdownOpen, setIsDialectDropdownOpen] = useState(false);

  const currentOption = DIALECT_OPTIONS.find((d) => d.id === selectedDialect) || DIALECT_OPTIONS[0];

  return (
    <header className="flex h-14 w-full items-center justify-between border-b border-white/5 bg-[#111216] px-3 sm:px-4 z-20">
      {/* Left: Mobile sidebar toggle & Dialect Selector */}
      <div className="flex items-center gap-2">
        <button
          onClick={onToggleSidebar}
          type="button"
          className="rounded-lg p-1.5 text-slate-400 hover:bg-canvas-elevated hover:text-white transition-colors md:hidden"
          title="Fungua menyu"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Dialect Selector Pill & Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsDialectDropdownOpen(!isDialectDropdownOpen)}
            type="button"
            className="flex items-center gap-1.5 rounded-full border border-canvas-border bg-canvas-surface/80 px-3 py-1.5 text-xs font-medium text-slate-200 hover:border-emerald-500/50 hover:bg-canvas-elevated transition-all"
          >
            <span>{currentOption.flag}</span>
            <span className="hidden sm:inline font-semibold">{currentOption.label}</span>
            <span className="sm:hidden font-semibold">{currentOption.label.split(' ')[0]}</span>
            <ChevronDown className="h-3.5 w-3.5 text-slate-400 ml-0.5" />
          </button>

          {isDialectDropdownOpen && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setIsDialectDropdownOpen(false)}
              />
              <div className="absolute left-0 mt-1.5 w-72 rounded-xl border border-canvas-border bg-[#0f1726] p-1.5 shadow-2xl z-50 animate-in fade-in zoom-in-95">
                <div className="px-3 py-1.5 text-[10px] font-mono uppercase tracking-wider text-slate-500 border-b border-canvas-border mb-1">
                  Chagua Lahaja ya Kiswahili
                </div>
                {DIALECT_OPTIONS.map((opt) => {
                  const isSelected = opt.id === selectedDialect;
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => {
                        onSelectDialect(opt.id);
                        setIsDialectDropdownOpen(false);
                      }}
                      className={`flex w-full items-start justify-between rounded-lg p-2 text-left text-xs transition-colors ${
                        isSelected
                          ? 'bg-emerald-500/15 text-emerald-200'
                          : 'text-slate-300 hover:bg-canvas-elevated hover:text-white'
                      }`}
                    >
                      <div className="flex gap-2">
                        <span className="text-base">{opt.flag}</span>
                        <div>
                          <div className="font-semibold flex items-center gap-1.5">
                            <span>{opt.label}</span>
                            <span className="text-[10px] font-normal text-slate-400">({opt.region})</span>
                          </div>
                          <p className="text-[11px] text-slate-400 font-mono mt-0.5">{opt.sample}</p>
                        </div>
                      </div>
                      {isSelected && <Check className="h-4 w-4 text-emerald-400 flex-shrink-0 mt-0.5" />}
                    </button>
                  );
                })}
              </div>
            </>
          )}
        </div>

        {/* System-2 Reasoning Toggle Button */}
        <button
          onClick={onToggleThinking}
          type="button"
          title="Washa au zima uchambuzi wa kina wa System-2 (<fikiri>)"
          className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1.5 text-xs font-mono font-medium transition-all ${
            includeThinking
              ? 'border-amber-500/50 bg-amber-500/15 text-amber-300 shadow-sm shadow-amber-950/40'
              : 'border-canvas-border bg-canvas-surface/60 text-slate-400 hover:text-slate-200 hover:bg-canvas-elevated'
          }`}
        >
          <BrainCircuit className={`h-3.5 w-3.5 ${includeThinking ? 'text-amber-400' : 'text-slate-500'}`} />
          <span className="hidden md:inline">Fikiri Kina (System-2)</span>
          <span className="md:hidden">&lt;fikiri&gt;</span>
        </button>
      </div>

      {/* Right: Free plan • Upgrade pill, WhatsApp toggle, M-Pesa balance badge, Cmd+K */}
      <div className="flex items-center gap-2">
        {/* "Free plan • Upgrade" Pill (from sample image) */}
        <button
          onClick={onOpenBilling}
          type="button"
          className="flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-zinc-300 hover:bg-white/10 hover:text-white transition-all shadow-sm"
        >
          <span className="text-zinc-400">Free plan</span>
          <span className="text-zinc-600">•</span>
          <span className="font-semibold text-white hover:underline">Upgrade</span>
        </button>

        {/* WhatsApp View Simulator Toggle */}
        <button
          onClick={onToggleViewMode}
          type="button"
          title={
            viewMode === 'whatsapp'
              ? 'Rejea kwenye mwonekano wa kawaida wa kiteknolojia'
              : 'Badili kwenda kiolesura chepesi cha WhatsApp Simulator (2G/Offline)'
          }
          className={`hidden sm:flex items-center gap-1.5 rounded-full border px-2.5 py-1.5 text-xs font-medium transition-all ${
            viewMode === 'whatsapp'
              ? 'border-[#00a884] bg-[#005c4b]/30 text-[#25d366] shadow-sm'
              : 'border-white/10 bg-white/5 text-zinc-400 hover:text-zinc-200 hover:bg-white/10'
          }`}
        >
          <Smartphone className={`h-3.5 w-3.5 ${viewMode === 'whatsapp' ? 'text-[#25d366]' : 'text-zinc-500'}`} />
          <span className="hidden lg:inline">
            {viewMode === 'whatsapp' ? 'WhatsApp Mode' : 'WhatsApp View'}
          </span>
        </button>

        {/* M-Pesa Balance Badge */}
        <button
          onClick={onOpenBilling}
          type="button"
          title="Ongeza salio la token kupitia Vodacom / Safaricom M-Pesa"
          className="flex items-center gap-1.5 rounded-full border border-emerald-500/25 bg-emerald-500/10 px-2.5 py-1.5 text-xs font-mono font-medium text-emerald-300 hover:border-emerald-500/50 hover:bg-emerald-500/20 transition-all"
        >
          <Coins className="h-3.5 w-3.5 text-emerald-400" />
          <span className="font-semibold">
            {balanceInfo ? balanceInfo.balance_tokens.toLocaleString() : '897,870'}
          </span>
          <span className="text-[10px] text-emerald-400/70 hidden md:inline">tokens</span>
        </button>

        {/* Cmd+K Palette button */}
        <button
          onClick={onOpenCommandPalette}
          type="button"
          className="hidden sm:flex items-center gap-1 rounded-lg border border-white/10 bg-white/5 px-2 py-1.5 text-xs text-zinc-400 hover:bg-white/10 hover:text-zinc-200 transition-colors"
          title="Fungua amri za haraka (Cmd+K)"
        >
          <Command className="h-3.5 w-3.5" />
          <span className="font-mono text-[10px]">K</span>
        </button>
      </div>
    </header>
  );
};
