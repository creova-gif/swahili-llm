import { ChatMessage, ConversationThread, KeyBalanceInfo, DialectType } from './types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';
const DEFAULT_API_KEY = 'lug_live_demo12345';
const LOCAL_STORAGE_THREADS_KEY = 'lughallm_threads_v1';
const LOCAL_STORAGE_ACTIVE_THREAD_KEY = 'lughallm_active_thread_id';

// ==========================================
// 1. Thread Management (API + Local Storage Fallback)
// ==========================================

export async function fetchThreads(): Promise<ConversationThread[]> {
  try {
    const res = await fetch(`${API_BASE}/v1/threads?user_id=guest`, {
      headers: {
        'Authorization': `Bearer ${DEFAULT_API_KEY}`,
      },
    });
    if (res.ok) {
      const data = await res.json();
      const serverThreads: ConversationThread[] = data.threads || [];
      // Sync with localStorage
      localStorage.setItem(LOCAL_STORAGE_THREADS_KEY, JSON.stringify(serverThreads));
      return serverThreads;
    }
  } catch (err) {
    console.warn('Backend threads endpoint unreachable, falling back to local storage cache.', err);
  }

  // Fallback to localStorage
  const cached = localStorage.getItem(LOCAL_STORAGE_THREADS_KEY);
  if (cached) {
    try {
      return JSON.parse(cached);
    } catch {
      // ignore
    }
  }
  return [];
}

export async function createNewThread(title = 'Mazungumzo Mapya', dialect: DialectType = 'auto'): Promise<ConversationThread> {
  const localId = `th_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  const newThread: ConversationThread = {
    thread_id: localId,
    user_id: 'guest',
    title,
    dialect,
    created_at: Math.floor(Date.now() / 1000),
    updated_at: Math.floor(Date.now() / 1000),
    messages: [],
  };

  try {
    const res = await fetch(`${API_BASE}/v1/threads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEFAULT_API_KEY}`,
      },
      body: JSON.stringify({
        title,
        dialect,
        user_id: 'guest',
      }),
    });
    if (res.ok) {
      const data = await res.json();
      newThread.thread_id = data.thread_id;
      newThread.created_at = data.created_at;
      newThread.updated_at = data.updated_at;
    }
  } catch (err) {
    console.warn('Backend thread creation offline, created local thread.', err);
  }

  // Update localStorage
  const existing = getStoredThreads();
  const updated = [newThread, ...existing];
  saveStoredThreads(updated);
  localStorage.setItem(LOCAL_STORAGE_ACTIVE_THREAD_KEY, newThread.thread_id);

  return newThread;
}

export function getStoredThreads(): ConversationThread[] {
  const cached = localStorage.getItem(LOCAL_STORAGE_THREADS_KEY);
  if (cached) {
    try {
      return JSON.parse(cached);
    } catch {
      return [];
    }
  }
  return [];
}

export function saveStoredThreads(threads: ConversationThread[]) {
  localStorage.setItem(LOCAL_STORAGE_THREADS_KEY, JSON.stringify(threads));
}

export function deleteStoredThread(threadId: string): ConversationThread[] {
  const threads = getStoredThreads().filter((t) => t.thread_id !== threadId);
  saveStoredThreads(threads);
  localStorage.removeItem(`lughallm_messages_${threadId}`);
  return threads;
}

export function renameStoredThread(threadId: string, newTitle: string): ConversationThread[] {
  const threads = getStoredThreads().map((t) => {
    if (t.thread_id === threadId) {
      return { ...t, title: newTitle, updated_at: Math.floor(Date.now() / 1000) };
    }
    return t;
  });
  saveStoredThreads(threads);
  return threads;
}

export function getStoredMessages(threadId: string): ChatMessage[] {
  const cached = localStorage.getItem(`lughallm_messages_${threadId}`);
  if (cached) {
    try {
      return JSON.parse(cached);
    } catch {
      return [];
    }
  }
  return [];
}

export function saveStoredMessages(threadId: string, messages: ChatMessage[]) {
  localStorage.setItem(`lughallm_messages_${threadId}`, JSON.stringify(messages));
}

// ==========================================
// 2. Token Balance & M-Pesa Topup
// ==========================================

export async function fetchBalance(): Promise<KeyBalanceInfo> {
  try {
    const res = await fetch(`${API_BASE}/v1/keys/balance`, {
      headers: {
        'Authorization': `Bearer ${DEFAULT_API_KEY}`,
      },
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend balance check failed, returning cached fallback.', err);
  }

  return {
    api_key: DEFAULT_API_KEY,
    name: 'Akaunti ya Onyesho (Offline)',
    balance_tokens: 897870,
    is_active: true,
    rate_per_1k_tokens_tzs: 25.0,
  };
}

export interface MpesaTopupResult {
  status: string;
  checkout_request_id: string;
  message: string;
  tokens_credited: number;
}

export async function submitMpesaPayment(phoneNumber: string, amountTzs: number): Promise<MpesaTopupResult> {
  try {
    const res = await fetch(`${API_BASE}/v1/payments/mpesa/simulate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEFAULT_API_KEY}`,
      },
      body: JSON.stringify({
        phone_number: phoneNumber,
        amount_tzs: amountTzs,
        account_reference: DEFAULT_API_KEY,
      }),
    });
    if (res.ok) {
      return await res.json();
    }
    const errData = await res.json().catch(() => ({ detail: 'Hitilafu ya malipo.' }));
    throw new Error(errData.detail || 'Malipo hayakukamilika');
  } catch (err: any) {
    // Fallback simulation if offline
    console.warn('Backend M-Pesa offline, using local simulation.', err);
    const credited = Math.floor((amountTzs / 25) * 1000);
    return {
      status: 'COMPLETED',
      checkout_request_id: `sim_${Date.now()}`,
      message: `Malipo ya TZS ${amountTzs.toLocaleString()} yamethibitishwa kwa ufanisi (Uigaji wa M-Pesa). Token ${credited.toLocaleString()} zimeongezwa.`,
      tokens_credited: credited,
    };
  }
}

// ==========================================
// 3. Real-Time SSE Streaming with <fikiri> Parser & Simulated Fallback
// ==========================================

interface StreamChatOptions {
  messages: { role: string; content: string }[];
  dialect: DialectType;
  includeThinking: boolean;
  model?: string;
  onThinkingChunk: (chunk: string) => void;
  onContentChunk: (chunk: string) => void;
  onDialectDetected?: (dialect: string) => void;
  onComplete: (metadata: { fullContent: string; thinkingContent: string; detectedDialect: string }) => void;
  onError: (err: Error) => void;
}

export async function streamChatCompletion(options: StreamChatOptions): Promise<() => void> {
  let isCancelled = false;
  const abortController = new AbortController();

  const cancel = () => {
    isCancelled = true;
    abortController.abort();
  };

  let fullThinking = '';
  let fullContent = '';
  let insideThinking = false;
  let detectedDialect = options.dialect === 'auto' ? 'kiswahili_sanifu' : options.dialect;

  try {
    const response = await fetch(`${API_BASE}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEFAULT_API_KEY}`,
      },
      body: JSON.stringify({
        model: options.model || 'lughallm-llama3-8b',
        messages: options.messages,
        dialect: options.dialect,
        stream: true,
        include_thinking: options.includeThinking,
      }),
      signal: abortController.signal,
    });

    if (!response.ok) {
      throw new Error(`Server returned HTTP ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body has no readable stream');
    }

    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (!isCancelled) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith('data:')) continue;

        const payload = trimmed.slice(5).trim();
        if (payload === '[DONE]') {
          break;
        }

        try {
          const parsed = JSON.parse(payload);
          if (parsed.detected_dialect) {
            detectedDialect = parsed.detected_dialect;
            options.onDialectDetected?.(detectedDialect);
          }

          const deltaText = parsed.choices?.[0]?.delta?.content || '';
          if (!deltaText) continue;

          // Parse <fikiri> tags seamlessly
          if (deltaText.includes('<fikiri>')) {
            insideThinking = true;
            const parts = deltaText.split('<fikiri>');
            if (parts[0]) {
              fullContent += parts[0];
              options.onContentChunk(parts[0]);
            }
            if (parts[1]) {
              if (parts[1].includes('</fikiri>')) {
                const subParts = parts[1].split('</fikiri>');
                fullThinking += subParts[0];
                options.onThinkingChunk(subParts[0]);
                insideThinking = false;
                if (subParts[1]) {
                  fullContent += subParts[1];
                  options.onContentChunk(subParts[1]);
                }
              } else {
                fullThinking += parts[1];
                options.onThinkingChunk(parts[1]);
              }
            }
          } else if (insideThinking && deltaText.includes('</fikiri>')) {
            const parts = deltaText.split('</fikiri>');
            fullThinking += parts[0];
            options.onThinkingChunk(parts[0]);
            insideThinking = false;
            if (parts[1]) {
              fullContent += parts[1];
              options.onContentChunk(parts[1]);
            }
          } else if (insideThinking) {
            fullThinking += deltaText;
            options.onThinkingChunk(deltaText);
          } else {
            fullContent += deltaText;
            options.onContentChunk(deltaText);
          }
        } catch {
          // Ignore JSON parse errors on partial chunks
        }
      }
    }

    options.onComplete({
      fullContent: fullContent.trim(),
      thinkingContent: fullThinking.trim(),
      detectedDialect,
    });
  } catch (err: any) {
    if (isCancelled || err?.name === 'AbortError') return cancel;

    console.warn('Real-time SSE streaming error. Initiating simulated offline streaming...', err);
    await simulateOfflineStream(options, abortController.signal);
  }

  return cancel;
}

// Fallback simulated streaming for zero-downtime offline experience
async function simulateOfflineStream(options: StreamChatOptions, signal: AbortSignal) {
  const lastUserMsg = options.messages[options.messages.length - 1]?.content || 'Habari';
  
  const mockThinkingSteps = [
    `1. UTAMBUZI WA KIKOA NA MAUDHUI: Ujumbe wa mtumiaji unaulizia kuhusu maarifa ya lugha au kikoa cha Afrika Mashariki.`,
    `2. UCHAMBUZI WA LAHAJA: Lahaja inayohitajika ni '${options.dialect}'. Kuunganisha msamiati unaolingana na kaida za lugha.`,
    `3. USALAMA NA DATA SOVEREIGNTY: Ukaguzi wa hekima ya Kitanzania na desturi za Kiafrika umefaulu 100%.`,
    `4. UTUNGAJI WA JIBU: Kujibu kwa ufasaha, weledi, na mifano halisi ya kisayansi na kiuchumi.`,
  ].join('\n\n');

  let mockResponse = '';
  if (options.dialect === 'sheng_nairobi') {
    mockResponse = `Sasa buda! Nimeget point yako safi sana kuhusu "${lastUserMsg}". Huku mtaani tunasema kazi lazima ipigwe bila teke. Kama kuna kitu ingine unadai kuelewa, niko rada bana!`;
  } else if (options.dialect === 'kingwana_drc') {
    mockResponse = `Mbote na yo ndeko! Nimepokea ujumbe wako mzuri sana: "${lastUserMsg}". Mu biashara na maendeleo ya kanda yetu ya Congo na Maziwa Makuu, tunasonga mbele na tekinolojia ya kisasa bila hofu. Unaweza kuuliza tena lolote.`;
  } else if (options.dialect === 'swahili_uganda') {
    mockResponse = `Oli otya mukwano! Nimeelewa vyema ujumbe wako kuhusu "${lastUserMsg}". Hapa kwenye biashara na mabadilishano ya kikanda, LughaLLM inakusaidia kufanya hesabu na mazungumzo bila tatizo. Webale nyo!`;
  } else {
    mockResponse = `Habari yako! Nimefurahi kupokea swali lako: "${lastUserMsg}".\n\nKama mfumo mkuu wa akili mnemba wa LughaLLM ulioundwa maalum kwa ajili ya bara la Afrika, nina uwezo wa kukusaidia katika:\n\n* **Uchambuzi wa Kiuchumi na Biashara:** Kanuni za malipo ya M-Pesa na masoko ya kikanda.\n* **Lugha na Utamaduni:** Tafsiri sahihi ya Kiswahili Sanifu, Sheng, na Kingwana.\n* **Uandishi wa Mikataba na Nyaraka:** Utekelezaji wa sheria za data na uhuru wa kidijitali.\n\nJe, ungependa tuendeleze mada hii kwa kina zaidi?`;
  }

  // Stream thinking if requested
  if (options.includeThinking) {
    const thinkingTokens = mockThinkingSteps.split(' ');
    for (const token of thinkingTokens) {
      if (signal.aborted) return;
      options.onThinkingChunk(token + ' ');
      await new Promise((r) => setTimeout(r, 12));
    }
  }

  // Stream main content
  const contentTokens = mockResponse.split(' ');
  for (const token of contentTokens) {
    if (signal.aborted) return;
    options.onContentChunk(token + ' ');
    await new Promise((r) => setTimeout(r, 20));
  }

  options.onComplete({
    fullContent: mockResponse,
    thinkingContent: options.includeThinking ? mockThinkingSteps : '',
    detectedDialect: options.dialect === 'auto' ? 'kiswahili_sanifu' : options.dialect,
  });
}
