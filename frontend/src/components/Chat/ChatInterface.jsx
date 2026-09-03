import React, { useState, useEffect } from 'react';
import { HiTrash, HiDocumentText, HiXMark, HiArrowDownTray } from 'react-icons/hi2';
import { useChatContext } from '../../context/ChatContext';
import { useApp } from '../../context/AppContext';
import { useKeyboardShortcuts } from '../../hooks/useKeyboardShortcuts';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

export const ChatInterface = () => {
  const { messages, clearMessages, activeClassification, removeClassification, sendMessage, isLoading } = useChatContext();
  const { jurisdiction, setActiveTab } = useApp();

  const exportConversation = () => {
    const exportData = {
      title: 'AyurPedia Conversation Export',
      exportedAt: new Date().toISOString(),
      jurisdiction,
      messages: messages.map(msg => ({
        sender: msg.sender,
        text: msg.text,
        timestamp: msg.timestamp,
        citations: msg.citations,
        confidence: msg.confidence
      }))
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ayurpedia-conversation-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Keyboard shortcuts
  useKeyboardShortcuts([
    { key: 'k', ctrlKey: true, callback: () => document.getElementById('chat-input')?.focus(), ignoreInInput: true },
    { key: 'e', ctrlKey: true, callback: exportConversation, ignoreInInput: true },
    { key: 'c', ctrlKey: true, shiftKey: true, callback: clearMessages, ignoreInInput: true },
  ]);

  return (
    <div className="max-w-5xl mx-auto px-3 sm:px-6 lg:px-8 py-3 sm:py-6">
    <div className="flex flex-col h-chat bg-[#fffdf8] dark:bg-primary-950/40 backdrop-blur-xl rounded-3xl border border-stone-200/80 dark:border-primary-900/50 shadow-card overflow-hidden transition-all duration-300 hover:shadow-lg">
      {/* Top Chat Toolbar */}
      <div className="flex items-center justify-between gap-2 px-3 sm:px-6 py-3 sm:py-3.5 bg-stone-50/80 dark:bg-primary-950/60 border-b border-stone-200/70 dark:border-primary-900/50 backdrop-blur-sm">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="relative w-2.5 h-2.5 rounded-full bg-emerald-500 pulse-ring shrink-0"></div>
          <div className="min-w-0">
            <h2 className="text-sm font-serif font-semibold text-stone-900 dark:text-stone-100 flex items-center gap-2 min-w-0">
              <span className="truncate"><span className="hidden sm:inline">Legal Intelligence </span>Session</span>
              <span className="text-[11px] font-semibold text-primary-800 bg-accent-100 dark:bg-accent-500/15 dark:text-accent-200 px-2 py-0.5 rounded-full border border-accent-300/50 dark:border-accent-500/30 shrink-0 badge-modern">
                {jurisdiction}
              </span>
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-1 sm:gap-2 shrink-0">
          {messages.length > 0 && (
            <button
              type="button"
              onClick={exportConversation}
              disabled={isLoading}
              title="Export conversation"
              className="flex items-center gap-1 px-2 py-1.5 text-xs font-semibold text-stone-500 hover:text-primary-800 hover:bg-accent-100/60 dark:hover:bg-primary-900/40 rounded-lg transition-all duration-200 cursor-pointer focus-premium card-lift"
            >
              <HiArrowDownTray className="w-4 h-4 icon-bounce" />
              <span className="hidden sm:inline">Export</span>
            </button>
          )}
          {messages.length > 1 && (
            <button
              type="button"
              onClick={clearMessages}
              disabled={isLoading}
              title="Clear chat history"
              className="flex items-center gap-1 px-2 py-1.5 text-xs font-semibold text-stone-500 hover:text-clay-600 hover:bg-clay-50 dark:hover:bg-clay-900/30 rounded-lg transition-all duration-200 cursor-pointer focus-premium card-lift"
            >
              <HiTrash className="w-4 h-4 icon-bounce" />
              <span className="hidden sm:inline">Clear Chat</span>
            </button>
          )}
        </div>
      </div>

      {/* Active Classification Context Banner */}
      {activeClassification && (
        <div className="flex items-center justify-between px-4 py-2.5 bg-accent-50 dark:bg-accent-500/10 border-b border-accent-200/70 dark:border-accent-500/30 text-xs text-stone-900 dark:text-stone-100 slide-in-top">
          <div className="flex items-center gap-2 overflow-hidden">
            <HiDocumentText className="w-4 h-4 text-accent-700 dark:text-accent-300 shrink-0 icon-bounce" />
            <span className="font-bold shrink-0">Active Context:</span>
            <span className="px-2 py-0.5 bg-primary-800 text-white rounded-md font-semibold text-[11px] shadow-sm badge-modern">
              {activeClassification.category}
            </span>
            <span className="text-stone-600 dark:text-stone-400 truncate text-[11px] hidden sm:inline">
              ({activeClassification.description})
            </span>
          </div>
          <button
            type="button"
            onClick={removeClassification}
            title="Remove classification from chat context"
            className="p-1 text-stone-500 hover:text-stone-800 dark:hover:text-stone-200 hover:bg-accent-100 dark:hover:bg-primary-900/40 rounded-md transition-all duration-200 cursor-pointer focus-premium card-lift"
          >
            <HiXMark className="w-4 h-4 icon-bounce" />
          </button>
        </div>
      )}

      {/* Messages Scroll Area */}
      <MessageList />

      {/* Input Area */}
      <div className="p-3 sm:p-4 bg-stone-50/80 dark:bg-primary-950/60 border-t border-stone-200/70 dark:border-primary-900/50 backdrop-blur-sm">
        <MessageInput />
      </div>
    </div>
    </div>
  );
};

export default ChatInterface;
