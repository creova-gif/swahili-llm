import React, { useState } from 'react';
import {
  X,
  CreditCard,
  Zap,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Smartphone,
  Globe,
  Coins,
} from 'lucide-react';
import { CurrencyOption, KeyBalanceInfo } from '../types';
import { submitMpesaPayment } from '../api';

interface BillingModalProps {
  isOpen: boolean;
  onClose: () => void;
  balanceInfo: KeyBalanceInfo | null;
  onBalanceUpdated: (newBalance: number) => void;
}

const CURRENCIES: CurrencyOption[] = [
  {
    code: 'TZS',
    name: 'Tanzania (Vodacom M-Pesa / Tigo Pesa)',
    flag: '🇹🇿',
    symbol: 'TZS',
    phonePrefix: '+255',
    conversionToTZS: 1.0,
    sampleAmounts: [1000, 2500, 5000, 10000, 25000],
  },
  {
    code: 'KES',
    name: 'Kenya (Safaricom M-Pesa)',
    flag: '🇰🇪',
    symbol: 'KES',
    phonePrefix: '+254',
    conversionToTZS: 20.0, // 1 KES = 20 TZS
    sampleAmounts: [50, 100, 250, 500, 1000],
  },
  {
    code: 'UGX',
    name: 'Uganda (MTN / Airtel Money)',
    flag: '🇺🇬',
    symbol: 'UGX',
    phonePrefix: '+256',
    conversionToTZS: 0.68, // 1 UGX = 0.68 TZS
    sampleAmounts: [2000, 5000, 10000, 20000, 50000],
  },
  {
    code: 'CDF',
    name: 'DR Congo (Vodacom M-Pesa DRC)',
    flag: '🇨🇩',
    symbol: 'CDF',
    phonePrefix: '+243',
    conversionToTZS: 0.95, // 1 CDF = 0.95 TZS
    sampleAmounts: [1000, 2500, 5000, 10000, 25000],
  },
  {
    code: 'RWF',
    name: 'Rwanda (MTN MoMo Rwanda)',
    flag: '🇷🇼',
    symbol: 'RWF',
    phonePrefix: '+250',
    conversionToTZS: 1.95, // 1 RWF = 1.95 TZS
    sampleAmounts: [500, 1000, 2500, 5000, 10000],
  },
];

export const BillingModal: React.FC<BillingModalProps> = ({
  isOpen,
  onClose,
  balanceInfo,
  onBalanceUpdated,
}) => {
  const [selectedCurrency, setSelectedCurrency] = useState<CurrencyOption>(CURRENCIES[1]); // KES default or TZS
  const [amount, setAmount] = useState<number>(selectedCurrency.sampleAmounts[1]);
  const [phoneNumber, setPhoneNumber] = useState('712345678');
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  if (!isOpen) return null;

  // Calculate equivalent in TZS and Tokens
  // Backend formula: rate is 25 TZS per 1000 tokens (i.e. 1 TZS = 40 tokens)
  const amountInTZS = amount * selectedCurrency.conversionToTZS;
  const tokensEarned = Math.round((amountInTZS / 25) * 1000);

  const handleSelectCurrency = (curr: CurrencyOption) => {
    setSelectedCurrency(curr);
    setAmount(curr.sampleAmounts[1]);
    setStatusMessage(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setStatusMessage(null);

    const fullPhone = `${selectedCurrency.phonePrefix}${phoneNumber.replace(/\D/g, '')}`;

    try {
      const result = await submitMpesaPayment(fullPhone, amountInTZS);
      setStatusMessage({
        type: 'success',
        text: result.message || `Malipo ya ${selectedCurrency.symbol} ${amount.toLocaleString()} yamethibitishwa!`,
      });

      if (balanceInfo) {
        onBalanceUpdated(balanceInfo.balance_tokens + result.tokens_credited);
      }
    } catch (err: any) {
      setStatusMessage({
        type: 'error',
        text: err.message || 'Hitilafu ya malipo ya M-Pesa. Tafadhali jaribu tena.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-lg rounded-2xl border border-canvas-border bg-[#0d1424] p-6 shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-canvas-border pb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              <CreditCard className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Ongeza Salio la Token (M-Pesa)</h2>
              <p className="text-xs text-slate-400">Pan-African Micro-Payments Gateway</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-canvas-elevated hover:text-white transition-colors"
            type="button"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Current Balance Card */}
        <div className="mt-4 rounded-xl border border-emerald-500/25 bg-gradient-to-r from-emerald-950/40 to-teal-950/30 p-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-[11px] font-mono uppercase tracking-wider text-emerald-400/90">
                Salio la Sasa (Token Ledger)
              </span>
              <div className="mt-1 flex items-baseline gap-2">
                <span className="text-2xl font-bold font-mono text-emerald-300">
                  {balanceInfo ? balanceInfo.balance_tokens.toLocaleString() : '897,870'}
                </span>
                <span className="text-xs text-emerald-400/70 font-mono">tokens</span>
              </div>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-slate-400 font-mono block">Kiwango cha Gharama:</span>
              <span className="text-xs font-mono text-slate-300">25 TZS / 1k tokens</span>
            </div>
          </div>
        </div>

        {/* Currency Selector Pills */}
        <div className="mt-5">
          <label className="text-xs font-semibold text-slate-300 mb-2 block flex items-center gap-1.5">
            <Globe className="w-3.5 h-3.5 text-slate-400" />
            Chagua Nchi & Njia ya Malipo:
          </label>
          <div className="grid grid-cols-5 gap-1.5">
            {CURRENCIES.map((curr) => {
              const isSelected = selectedCurrency.code === curr.code;
              return (
                <button
                  key={curr.code}
                  type="button"
                  onClick={() => handleSelectCurrency(curr)}
                  className={`flex flex-col items-center justify-center p-2 rounded-lg border text-center transition-all ${
                    isSelected
                      ? 'border-emerald-500 bg-emerald-500/15 text-emerald-300 shadow-sm'
                      : 'border-canvas-border bg-canvas-surface/60 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                  }`}
                >
                  <span className="text-lg">{curr.flag}</span>
                  <span className="text-xs font-bold font-mono mt-0.5">{curr.code}</span>
                </button>
              );
            })}
          </div>
          <p className="mt-1 text-[11px] text-slate-400 truncate">{selectedCurrency.name}</p>
        </div>

        {/* Quick Amount Options */}
        <div className="mt-4">
          <label className="text-xs font-semibold text-slate-300 mb-2 block flex items-center gap-1.5">
            <Coins className="w-3.5 h-3.5 text-slate-400" />
            Kiasi cha Kuongeza ({selectedCurrency.symbol}):
          </label>
          <div className="grid grid-cols-5 gap-1.5">
            {selectedCurrency.sampleAmounts.map((amt) => {
              const isSelected = amount === amt;
              return (
                <button
                  key={amt}
                  type="button"
                  onClick={() => setAmount(amt)}
                  className={`rounded-lg py-2 px-1 text-center font-mono text-xs font-medium border transition-all ${
                    isSelected
                      ? 'border-emerald-500 bg-emerald-500/20 text-emerald-300 shadow-sm'
                      : 'border-canvas-border bg-canvas-input text-slate-300 hover:border-slate-600'
                  }`}
                >
                  {amt.toLocaleString()}
                </button>
              );
            })}
          </div>
        </div>

        {/* Token Calculation Preview */}
        <div className="mt-4 rounded-lg bg-black/40 border border-slate-800 p-3 flex items-center justify-between text-xs font-mono">
          <span className="text-slate-400">Utapokea jumla ya:</span>
          <span className="text-emerald-400 font-bold text-sm flex items-center gap-1">
            <Zap className="w-3.5 h-3.5 fill-emerald-400" />
            +{tokensEarned.toLocaleString()} tokens
          </span>
        </div>

        {/* Form: Phone number & Daraja STK Push trigger */}
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 mb-1.5 block flex items-center gap-1.5">
              <Smartphone className="w-3.5 h-3.5 text-slate-400" />
              Nambari ya Simu ya M-Pesa:
            </label>
            <div className="flex rounded-lg overflow-hidden border border-canvas-border focus-within:border-emerald-500">
              <span className="bg-canvas-elevated px-3 py-2 text-xs font-mono text-slate-300 flex items-center border-r border-canvas-border">
                {selectedCurrency.phonePrefix}
              </span>
              <input
                type="tel"
                required
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="712345678"
                className="flex-1 bg-canvas-input px-3 py-2 text-xs font-mono text-white placeholder-slate-500 focus:outline-none"
              />
            </div>
            <p className="mt-1 text-[10px] text-slate-500">
              STK Push PIN prompt itatumwa kwenye simu yako mara moja.
            </p>
          </div>

          {/* Feedback messages */}
          {statusMessage && (
            <div
              className={`rounded-lg p-3 text-xs flex items-start gap-2 border ${
                statusMessage.type === 'success'
                  ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
                  : 'bg-rose-950/40 border-rose-500/40 text-rose-300'
              }`}
            >
              {statusMessage.type === 'success' ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
              )}
              <span className="leading-relaxed">{statusMessage.text}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || amount <= 0}
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 py-3 text-xs font-bold text-white shadow-lg shadow-emerald-950/50 hover:from-emerald-500 hover:to-teal-500 active:scale-[0.99] disabled:opacity-50 transition-all"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Inatuma Ombi la Daraja STK Push...</span>
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 fill-white" />
                <span>
                  Lipa {selectedCurrency.symbol} {amount.toLocaleString()} kupitia M-Pesa
                </span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
