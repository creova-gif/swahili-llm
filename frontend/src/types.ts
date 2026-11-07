export type DialectType = 
  | 'auto'
  | 'kiswahili_sanifu'
  | 'sheng_nairobi'
  | 'kingwana_drc'
  | 'swahili_uganda'
  | 'coastal_swahili';

export interface DialectOption {
  id: DialectType;
  label: string;
  region: string;
  flag: string;
  sample: string;
  tagline: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  thinkingContent?: string;
  reasoningTokens?: number;
  thinkingDurationMs?: number;
  detectedDialect?: string;
  timestamp: string;
  isStreaming?: boolean;
}

export interface ConversationThread {
  thread_id: string;
  user_id: string;
  title: string;
  dialect: string;
  created_at: number;
  updated_at: number;
  messages?: ChatMessage[];
}

export interface KeyBalanceInfo {
  api_key: string;
  name: string;
  balance_tokens: number;
  is_active: boolean;
  rate_per_1k_tokens_tzs: number;
}

export interface CurrencyOption {
  code: 'TZS' | 'KES' | 'UGX' | 'CDF' | 'RWF';
  name: string;
  flag: string;
  symbol: string;
  phonePrefix: string;
  conversionToTZS: number; // 1 unit of this currency = X TZS
  sampleAmounts: number[];
}

export type ViewMode = 'enterprise' | 'whatsapp';
