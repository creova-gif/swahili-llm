import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  ChatMessage,
  ConversationThread,
  DialectType,
  KeyBalanceInfo,
  ViewMode,
} from './types';
import {
  fetchThreads,
  createNewThread,
  deleteStoredThread,
  renameStoredThread,
  getStoredMessages,
  saveStoredMessages,
  fetchBalance,
  streamChatCompletion,
} from './api';
import { Header } from './components/Header';
import { ThreadSidebar } from './components/ThreadSidebar';
import { ChatStream } from './components/ChatStream';
import { BillingModal } from './components/BillingModal';
import { CommandPalette } from './components/CommandPalette';

export const App: React.FC = () => {
  const [threads, setThreads] = useState<ConversationThread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [selectedDialect, setSelectedDialect] = useState<DialectType>('auto');
  const [includeThinking, setIncludeThinking] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('enterprise');
  const [balanceInfo, setBalanceInfo] = useState<KeyBalanceInfo | null>(null);

  // Modals & Panels
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isBillingOpen, setIsBillingOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);

  // Active stream cancel ref
  const cancelStreamRef = useRef<(() => void) | null>(null);

  // Initialize Threads & Balance
  useEffect(() => {
    async function init() {
      const loadedThreads = await fetchThreads();
      setThreads(loadedThreads);

      if (loadedThreads.length > 0) {
        const lastActiveId = localStorage.getItem('lughallm_active_thread_id');
        const targetThread = loadedThreads.find((t) => t.thread_id === lastActiveId) || loadedThreads[0];
        setActiveThreadId(targetThread.thread_id);
        const storedMsgs = getStoredMessages(targetThread.thread_id);
        setMessages(storedMsgs);
      } else {
        // Create initial thread
        const initial = await createNewThread('Mazungumzo Mapya', 'auto');
        setThreads([initial]);
        setActiveThreadId(initial.thread_id);
        setMessages([]);
      }

      const balance = await fetchBalance();
      setBalanceInfo(balance);
    }

    init();
  }, []);

  // Global Keyboard Shortcuts (Cmd+K, Cmd+O, Cmd+B)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isCmdOrCtrl = e.metaKey || e.ctrlKey;
      if (isCmdOrCtrl && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      } else if (isCmdOrCtrl && e.key.toLowerCase() === 'o') {
        e.preventDefault();
        handleNewChat();
      } else if (isCmdOrCtrl && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        setIsBillingOpen(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [threads]);

  // Handle switching active thread
  const handleSelectThread = useCallback((threadId: string) => {
    if (cancelStreamRef.current) {
      cancelStreamRef.current();
      cancelStreamRef.current = null;
      setIsStreaming(false);
    }
    setActiveThreadId(threadId);
    localStorage.setItem('lughallm_active_thread_id', threadId);
    const msgs = getStoredMessages(threadId);
    setMessages(msgs);
  }, []);

  // Handle creating a new chat
  const handleNewChat = useCallback(async () => {
    if (cancelStreamRef.current) {
      cancelStreamRef.current();
      cancelStreamRef.current = null;
      setIsStreaming(false);
    }
    const newThread = await createNewThread('Mazungumzo Mapya', selectedDialect);
    setThreads((prev) => [newThread, ...prev]);
    setActiveThreadId(newThread.thread_id);
    setMessages([]);
  }, [selectedDialect]);

  // Handle thread deletion
  const handleDeleteThread = useCallback(
    (threadId: string) => {
      const remaining = deleteStoredThread(threadId);
      setThreads(remaining);
      if (activeThreadId === threadId) {
        if (remaining.length > 0) {
          handleSelectThread(remaining[0].thread_id);
        } else {
          handleNewChat();
        }
      }
    },
    [activeThreadId, handleSelectThread, handleNewChat]
  );

  // Handle thread renaming
  const handleRenameThread = useCallback((threadId: string, newTitle: string) => {
    const updated = renameStoredThread(threadId, newTitle);
    setThreads(updated);
  }, []);

  // Handle clearing messages in current thread
  const handleClearCurrentChat = useCallback(() => {
    if (activeThreadId) {
      setMessages([]);
      saveStoredMessages(activeThreadId, []);
    }
  }, [activeThreadId]);

  // Handle sending a message with real-time SSE token streaming
  const handleSendMessage = useCallback(
    async (userText: string) => {
      if (!userText.trim() || isStreaming || !activeThreadId) return;

      const userMsgId = `msg_${Date.now()}_u`;
      const asstMsgId = `msg_${Date.now() + 1}_a`;
      const nowStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      const userMessage: ChatMessage = {
        id: userMsgId,
        role: 'user',
        content: userText,
        timestamp: nowStr,
      };

      const assistantMessage: ChatMessage = {
        id: asstMsgId,
        role: 'assistant',
        content: '',
        thinkingContent: '',
        timestamp: nowStr,
        isStreaming: true,
      };

      const updatedMessages = [...messages, userMessage, assistantMessage];
      setMessages(updatedMessages);
      setIsStreaming(true);

      // Auto-update thread title if this is the first turn
      if (messages.length === 0) {
        const titleSnippet = userText.slice(0, 32) + (userText.length > 32 ? '...' : '');
        handleRenameThread(activeThreadId, titleSnippet);
      }

      // Format messages history for the LLM API
      const conversationHistory = updatedMessages
        .slice(0, -1)
        .map((m) => ({ role: m.role, content: m.content }));

      const streamStartTime = Date.now();

      const cancelFn = await streamChatCompletion({
        messages: conversationHistory,
        dialect: selectedDialect,
        includeThinking,
        onThinkingChunk: (chunk: string) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === asstMsgId
                ? { ...msg, thinkingContent: (msg.thinkingContent || '') + chunk }
                : msg
            )
          );
        },
        onContentChunk: (chunk: string) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === asstMsgId ? { ...msg, content: msg.content + chunk } : msg
            )
          );
        },
        onDialectDetected: (detected: string) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === asstMsgId ? { ...msg, detectedDialect: detected } : msg
            )
          );
        },
        onComplete: (meta) => {
          const duration = Date.now() - streamStartTime;
          setIsStreaming(false);
          cancelStreamRef.current = null;

          setMessages((prev) => {
            const finalMessages = prev.map((msg) =>
              msg.id === asstMsgId
                ? {
                    ...msg,
                    content: meta.fullContent,
                    thinkingContent: meta.thinkingContent,
                    detectedDialect: meta.detectedDialect,
                    thinkingDurationMs: duration,
                    isStreaming: false,
                  }
                : msg
            );
            saveStoredMessages(activeThreadId, finalMessages);
            return finalMessages;
          });

          // Refresh token ledger balance
          fetchBalance().then(setBalanceInfo).catch(console.warn);
        },
        onError: (err) => {
          console.error('Chat stream error:', err);
          setIsStreaming(false);
          cancelStreamRef.current = null;
        },
      });

      cancelStreamRef.current = cancelFn;
    },
    [activeThreadId, isStreaming, messages, selectedDialect, includeThinking, handleRenameThread]
  );

  const handleStopStreaming = useCallback(() => {
    if (cancelStreamRef.current) {
      cancelStreamRef.current();
      cancelStreamRef.current = null;
      setIsStreaming(false);
      setMessages((prev) =>
        prev.map((msg) => (msg.isStreaming ? { ...msg, isStreaming: false } : msg))
      );
    }
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-canvas text-slate-100 font-sans">
      {/* Thread History Sidebar */}
      <ThreadSidebar
        threads={threads}
        activeThreadId={activeThreadId}
        onSelectThread={handleSelectThread}
        onNewChat={handleNewChat}
        onRenameThread={handleRenameThread}
        onDeleteThread={handleDeleteThread}
        isOpen={isSidebarOpen}
        onCloseMobile={() => setIsSidebarOpen(false)}
      />

      {/* Main Chat Area */}
      <div className="flex flex-1 flex-col h-full overflow-hidden">
        {/* Header */}
        <Header
          onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
          selectedDialect={selectedDialect}
          onSelectDialect={setSelectedDialect}
          includeThinking={includeThinking}
          onToggleThinking={() => setIncludeThinking((prev) => !prev)}
          viewMode={viewMode}
          onToggleViewMode={() =>
            setViewMode((prev) => (prev === 'enterprise' ? 'whatsapp' : 'enterprise'))
          }
          balanceInfo={balanceInfo}
          onOpenBilling={() => setIsBillingOpen(true)}
          onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
        />

        {/* Chat Stream View */}
        <ChatStream
          messages={messages}
          isStreaming={isStreaming}
          viewMode={viewMode}
          selectedDialect={selectedDialect}
          onSendMessage={handleSendMessage}
          onStopStreaming={handleStopStreaming}
        />
      </div>

      {/* M-Pesa Multi-Currency Billing Slide-over / Modal */}
      <BillingModal
        isOpen={isBillingOpen}
        onClose={() => setIsBillingOpen(false)}
        balanceInfo={balanceInfo}
        onBalanceUpdated={(newBal) => {
          setBalanceInfo((prev) => (prev ? { ...prev, balance_tokens: newBal } : null));
        }}
      />

      {/* Cmd+K Command Palette */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onNewChat={handleNewChat}
        onOpenBilling={() => setIsBillingOpen(true)}
        onSelectDialect={setSelectedDialect}
        onToggleWhatsApp={() =>
          setViewMode((prev) => (prev === 'enterprise' ? 'whatsapp' : 'enterprise'))
        }
        onToggleThinking={() => setIncludeThinking((prev) => !prev)}
        onClearChat={handleClearCurrentChat}
        isWhatsApp={viewMode === 'whatsapp'}
        includeThinking={includeThinking}
        currentDialect={selectedDialect}
      />
    </div>
  );
};

export default App;
