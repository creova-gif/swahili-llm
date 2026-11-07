import React, { useState } from 'react';
import {
  MessageSquare,
  Plus,
  Trash2,
  Edit2,
  Check,
  X,
  Search,
  ShieldCheck,
  Server,
  Zap,
} from 'lucide-react';
import { ConversationThread } from '../types';

interface ThreadSidebarProps {
  threads: ConversationThread[];
  activeThreadId: string | null;
  onSelectThread: (threadId: string) => void;
  onNewChat: () => void;
  onRenameThread: (threadId: string, newTitle: string) => void;
  onDeleteThread: (threadId: string) => void;
  isOpen: boolean;
  onCloseMobile?: () => void;
}

export const ThreadSidebar: React.FC<ThreadSidebarProps> = ({
  threads,
  activeThreadId,
  onSelectThread,
  onNewChat,
  onRenameThread,
  onDeleteThread,
  isOpen,
  onCloseMobile,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [editingThreadId, setEditingThreadId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const filteredThreads = threads.filter((t) =>
    (t.title || 'Mazungumzo').toLowerCase().includes(searchQuery.toLowerCase())
  );

  const startEditing = (t: ConversationThread, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingThreadId(t.thread_id);
    setEditTitle(t.title || 'Mazungumzo');
  };

  const saveRename = (threadId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (editTitle.trim()) {
      onRenameThread(threadId, editTitle.trim());
    }
    setEditingThreadId(null);
  };

  const cancelRename = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingThreadId(null);
  };

  const handleDelete = (threadId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Una uhakika unataka kufuta mazungumzo haya?')) {
      onDeleteThread(threadId);
    }
  };

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-30 flex flex-col w-72 bg-[#0a0f1d] border-r border-canvas-border transition-transform duration-200 ease-in-out md:static md:translate-x-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      {/* Top Header / Brand */}
      <div className="flex items-center justify-between p-4 border-b border-canvas-border">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <Zap className="h-4 w-4 fill-emerald-400" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-1.5">
              <span>LughaLLM</span>
              <span className="text-[10px] font-mono font-medium px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                PRO
              </span>
            </h1>
            <p className="text-[11px] text-slate-400 font-mono">Pan-African AI Model</p>
          </div>
        </div>

        {onCloseMobile && (
          <button
            onClick={onCloseMobile}
            className="md:hidden p-1 text-slate-400 hover:text-slate-200"
            type="button"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* "+ Mazungumzo Mapya" (New Chat) Button */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          type="button"
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 px-3.5 py-2.5 text-xs font-semibold text-white shadow-lg shadow-emerald-950/50 hover:from-emerald-500 hover:to-teal-500 active:scale-[0.98] transition-all"
        >
          <Plus className="h-4 w-4" />
          <span>+ Mazungumzo Mapya</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="px-3 pb-2">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-500" />
          <input
            type="text"
            placeholder="Tafuta mazungumzo..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-md bg-canvas-input py-1.5 pl-8 pr-3 text-xs text-slate-200 placeholder-slate-500 border border-canvas-border focus:border-emerald-500/50 focus:outline-none"
          />
        </div>
      </div>

      {/* Thread List */}
      <div className="flex-1 overflow-y-auto px-2 py-1 space-y-1">
        <div className="px-2 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
          Historia ya Mazungumzo ({filteredThreads.length})
        </div>

        {filteredThreads.length === 0 ? (
          <div className="px-3 py-8 text-center text-xs text-slate-500">
            Hakuna mazungumzo yaliyopatikana. Bonyeza kitufe cha juu kuanza jipya!
          </div>
        ) : (
          filteredThreads.map((thread) => {
            const isActive = thread.thread_id === activeThreadId;
            const isEditing = thread.thread_id === editingThreadId;

            return (
              <div
                key={thread.thread_id}
                onClick={() => {
                  if (!isEditing) {
                    onSelectThread(thread.thread_id);
                    onCloseMobile?.();
                  }
                }}
                className={`group relative flex items-center justify-between rounded-lg px-2.5 py-2 text-xs cursor-pointer transition-all ${
                  isActive
                    ? 'bg-emerald-500/15 text-emerald-200 border border-emerald-500/30'
                    : 'text-slate-300 hover:bg-canvas-elevated hover:text-white border border-transparent'
                }`}
              >
                <div className="flex items-center gap-2 min-w-0 flex-1 mr-1">
                  <MessageSquare
                    className={`h-3.5 w-3.5 flex-shrink-0 ${
                      isActive ? 'text-emerald-400' : 'text-slate-500 group-hover:text-slate-400'
                    }`}
                  />

                  {isEditing ? (
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                      className="w-full rounded bg-canvas-input px-1.5 py-0.5 text-xs text-white border border-emerald-500 focus:outline-none"
                      autoFocus
                    />
                  ) : (
                    <span className="truncate font-medium">{thread.title || 'Mazungumzo Mapya'}</span>
                  )}
                </div>

                {/* Actions: Edit & Delete */}
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {isEditing ? (
                    <>
                      <button
                        onClick={(e) => saveRename(thread.thread_id, e)}
                        className="p-1 hover:text-emerald-400 text-slate-400"
                        title="Hifadhi jina"
                        type="button"
                      >
                        <Check className="h-3 w-3" />
                      </button>
                      <button
                        onClick={cancelRename}
                        className="p-1 hover:text-rose-400 text-slate-400"
                        title="Ghairi"
                        type="button"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={(e) => startEditing(thread, e)}
                        className="p-1 hover:text-slate-200 text-slate-500"
                        title="Badilisha jina"
                        type="button"
                      >
                        <Edit2 className="h-3 w-3" />
                      </button>
                      <button
                        onClick={(e) => handleDelete(thread.thread_id, e)}
                        className="p-1 hover:text-rose-400 text-slate-500"
                        title="Futa mazungumzo"
                        type="button"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Bottom Sovereign & Offline Status Footprint */}
      <div className="p-3 border-t border-canvas-border bg-[#080c17]">
        <div className="rounded-lg border border-emerald-500/20 bg-emerald-950/20 p-2.5 text-[11px] text-emerald-300/90 space-y-1">
          <div className="flex items-center gap-1.5 font-semibold text-emerald-300">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            <span>Air-Gapped Sovereign AI</span>
          </div>
          <p className="text-[10px] text-slate-400 leading-tight">
            Data haivuji nje ya mipaka ya Afrika Mashariki (EAC PDPC / DPA Compliant).
          </p>
          <div className="pt-1 flex items-center gap-1 text-[10px] text-slate-500 font-mono">
            <Server className="h-3 w-3 text-slate-400" />
            <span>NVIDIA NIM / Edge GGUF</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
