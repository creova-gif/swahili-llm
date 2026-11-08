import React, { useState } from 'react';
import {
  Plus,
  Trash2,
  Edit2,
  Check,
  X,
  Search,
  MessageSquare,
  Folder,
  BookOpen,
  Code2,
  Compass,
  Sparkles,
  Settings,
  PanelLeftClose,
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
  onOpenBilling?: () => void;
  onOpenCommandPalette?: () => void;
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
  onOpenBilling,
  onOpenCommandPalette,
}) => {
  const [editingThreadId, setEditingThreadId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const filteredThreads = threads;

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
      className={`fixed inset-y-0 left-0 z-30 flex flex-col w-[260px] bg-[#17181d] border-r border-white/5 transition-transform duration-200 ease-in-out md:static md:translate-x-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      {/* Top Header: Brand Logo & Collapse Toggle */}
      <div className="flex items-center justify-between px-4 pt-4 pb-2">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-white/10 text-white font-bold">
            <Zap className="h-4 w-4 fill-white text-white" />
          </div>
          <span className="font-semibold text-sm tracking-tight text-white">LughaLLM</span>
        </div>

        <button
          onClick={onCloseMobile}
          type="button"
          className="text-zinc-400 hover:text-white p-1 rounded-md hover:bg-white/5 transition-colors"
          title="Funga menyu"
        >
          <PanelLeftClose className="h-4 w-4" />
        </button>
      </div>

      {/* "+ New chat" Button */}
      <div className="px-3 py-2">
        <button
          onClick={onNewChat}
          type="button"
          className="flex w-full items-center gap-2.5 rounded-lg bg-[#22242c] px-3.5 py-2 text-xs font-medium text-zinc-200 border border-white/5 hover:bg-[#282a34] hover:text-white transition-all shadow-sm"
        >
          <Plus className="h-3.5 w-3.5 text-zinc-400" />
          <span>New chat</span>
        </button>
      </div>

      {/* Core Navigation Items */}
      <div className="px-2 py-1 space-y-0.5">
        <button
          onClick={onOpenCommandPalette}
          type="button"
          className="flex w-full items-center justify-between rounded-lg px-2.5 py-1.5 text-xs text-zinc-400 hover:bg-white/5 hover:text-zinc-200 transition-colors"
        >
          <div className="flex items-center gap-2.5">
            <Search className="h-3.5 w-3.5 text-zinc-500" />
            <span>Search</span>
          </div>
          <kbd className="font-mono text-[10px] text-zinc-600 bg-white/5 px-1 rounded">⌘K</kbd>
        </button>

        <button
          type="button"
          className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-1.5 text-xs text-zinc-200 bg-white/5 font-medium transition-colors"
        >
          <MessageSquare className="h-3.5 w-3.5 text-emerald-400" />
          <span>Chats</span>
        </button>

        <button
          type="button"
          className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-1.5 text-xs text-zinc-400 hover:bg-white/5 hover:text-zinc-200 transition-colors"
        >
          <Folder className="h-3.5 w-3.5 text-zinc-500" />
          <span>Projects</span>
        </button>

        <button
          type="button"
          className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-1.5 text-xs text-zinc-400 hover:bg-white/5 hover:text-zinc-200 transition-colors"
        >
          <BookOpen className="h-3.5 w-3.5 text-zinc-500" />
          <span>Library</span>
        </button>

        <button
          type="button"
          className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-1.5 text-xs text-zinc-400 hover:bg-white/5 hover:text-zinc-200 transition-colors"
        >
          <Code2 className="h-3.5 w-3.5 text-zinc-500" />
          <span>Code</span>
        </button>
      </div>

      {/* Middle Scrollable Section: GPTs, Projects & Recents */}
      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-4 text-xs">
        {/* GPTs Category */}
        <div>
          <div className="px-2.5 pb-1 text-[10px] font-medium uppercase tracking-wider text-zinc-500">
            GPTs
          </div>
          <button
            type="button"
            className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-1.5 text-zinc-400 hover:bg-white/5 hover:text-zinc-200 transition-colors"
          >
            <Compass className="h-3.5 w-3.5 text-zinc-500" />
            <span>Explore GPTs</span>
          </button>
        </div>

        {/* Projects Category */}
        <div>
          <div className="px-2.5 pb-1 text-[10px] font-medium uppercase tracking-wider text-zinc-500">
            Projects
          </div>
          <div className="space-y-0.5">
            <button
              type="button"
              className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-1.5 text-zinc-400 hover:bg-white/5 hover:text-zinc-200 transition-colors"
            >
              <Folder className="h-3.5 w-3.5 text-zinc-500" />
              <span>Content Plan</span>
            </button>
            <button
              type="button"
              className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-1.5 text-zinc-400 hover:bg-white/5 hover:text-zinc-200 transition-colors"
            >
              <Folder className="h-3.5 w-3.5 text-zinc-500" />
              <span>Wellness Plan</span>
            </button>
          </div>
        </div>

        {/* Recents Category */}
        <div>
          <div className="px-2.5 pb-1 text-[10px] font-medium uppercase tracking-wider text-zinc-500">
            Recents
          </div>

          {filteredThreads.length === 0 ? (
            <div className="px-2.5 py-3 text-zinc-500 text-[11px]">
              No recent chats.
            </div>
          ) : (
            <div className="space-y-0.5">
              {filteredThreads.map((thread) => {
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
                    className={`group relative flex items-center justify-between rounded-lg px-2.5 py-1.5 cursor-pointer transition-all ${
                      isActive
                        ? 'bg-[#22242c] text-white font-medium'
                        : 'text-zinc-400 hover:bg-white/5 hover:text-zinc-200'
                    }`}
                  >
                    <span className="truncate pr-2">{thread.title || 'New Chat'}</span>

                    {/* Actions: Rename / Delete */}
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      {isEditing ? (
                        <>
                          <button
                            onClick={(e) => saveRename(thread.thread_id, e)}
                            className="p-0.5 hover:text-emerald-400 text-zinc-400"
                            type="button"
                          >
                            <Check className="h-3 w-3" />
                          </button>
                          <button
                            onClick={cancelRename}
                            className="p-0.5 hover:text-rose-400 text-zinc-400"
                            type="button"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            onClick={(e) => startEditing(thread, e)}
                            className="p-0.5 hover:text-zinc-200 text-zinc-500"
                            type="button"
                          >
                            <Edit2 className="h-3 w-3" />
                          </button>
                          <button
                            onClick={(e) => handleDelete(thread.thread_id, e)}
                            className="p-0.5 hover:text-rose-400 text-zinc-500"
                            type="button"
                          >
                            <Trash2 className="h-3 w-3" />
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Bottom Upgrade / Trial Card (from sample UI) */}
      <div className="p-3">
        <div className="rounded-xl border border-white/10 bg-[#1f2129] p-3 text-xs space-y-2.5">
          <div className="flex items-center gap-1.5 text-zinc-200 font-semibold">
            <Sparkles className="h-3.5 w-3.5 text-amber-400" />
            <span>Lumen AI Trial</span>
          </div>
          <p className="text-[11px] text-zinc-400 leading-relaxed">
            There are 10 days left for you to enjoy the various features.
          </p>
          <button
            onClick={onOpenBilling}
            type="button"
            className="w-full rounded-lg bg-white px-3 py-1.5 text-xs font-semibold text-black hover:bg-zinc-200 active:scale-[0.98] transition-all"
          >
            Upgrade to Pro
          </button>
        </div>
      </div>

      {/* User Profile Row at bottom */}
      <div className="p-3 border-t border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-amber-500 to-rose-500 flex items-center justify-center text-white text-xs font-bold overflow-hidden ring-1 ring-white/10">
            <span>MH</span>
          </div>
          <div className="text-left">
            <div className="text-xs font-semibold text-zinc-200">Mithila Haque</div>
            <div className="text-[10px] text-zinc-500">mithila@creova.ai</div>
          </div>
        </div>

        <button
          onClick={onOpenCommandPalette}
          type="button"
          className="text-zinc-500 hover:text-zinc-200 p-1 rounded-md hover:bg-white/5 transition-colors"
          title="Mipangilio"
        >
          <Settings className="h-4 w-4" />
        </button>
      </div>
    </aside>
  );
};

