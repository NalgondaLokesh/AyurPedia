import React from 'react';
import { useChatContext } from '../../context/ChatContext';
import { useApp } from '../../context/AppContext';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { HiTrash, HiDocumentText, HiXMark, HiSparkles, HiShieldCheck } from 'react-icons/hi2';

export const ChatInterface = () => {
  const { messages, clearMessages, activeClassification, removeClassification, sendMessage, isLoading } = useChatContext();
  const { jurisdiction, setActiveTab } = useApp();

  const QUICK_QUESTIONS = [
    { text: 'What is Section 3(p) under the Indian Patents Act 1970?', tag: 'Patents' },
    { text: 'What are the disclosure requirements under WIPO GRATK Treaty 2024?', tag: 'WIPO' },
    { text: 'What are the rules for FSSAI Ayurveda-Aahar approval?', tag: 'Food / Aahar' },
    { text: 'When is National Biodiversity Authority (NBA) approval needed?', tag: 'NBA' },
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-5xl mx-auto bg-stone-50/50 backdrop-blur-md rounded-3xl border border-stone-200/90 shadow-glass overflow-hidden">
      {/* Top Chat Toolbar */}
      <div className="flex items-center justify-between px-4 sm:px-6 py-3 bg-white/80 border-b border-stone-200/80 backdrop-blur-xs">
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
          <div>
            <h2 className="text-xs sm:text-sm font-bold text-stone-900 flex items-center gap-2">
              <span>Ayurvedic Legal Intelligence Session</span>
              <span className="text-[11px] font-semibold text-primary-700 bg-primary-50 px-2 py-0.5 rounded-full border border-primary-200">
                {jurisdiction} Mode
              </span>
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {messages.length > 1 && (
            <button
              type="button"
              onClick={clearMessages}
              disabled={isLoading}
              title="Clear chat history"
              className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold text-stone-500 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer"
            >
              <HiTrash className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Clear Chat</span>
            </button>
          )}
        </div>
      </div>

      {/* Active Classification Context Banner */}
      {activeClassification && (
        <div className="flex items-center justify-between px-4 py-2 bg-emerald-50 border-b border-emerald-200 text-xs text-primary-950 animate-in fade-in duration-150">
          <div className="flex items-center gap-2 overflow-hidden">
            <HiDocumentText className="w-4 h-4 text-primary-700 shrink-0" />
            <span className="font-bold shrink-0">Active Context:</span>
            <span className="px-2 py-0.5 bg-primary-700 text-white rounded-md font-semibold text-[11px]">
              {activeClassification.category}
            </span>
            <span className="text-stone-600 truncate text-[11px] hidden sm:inline">
              ({activeClassification.description})
            </span>
          </div>
          <button
            type="button"
            onClick={removeClassification}
            title="Remove classification from chat context"
            className="p-1 text-stone-500 hover:text-stone-800 hover:bg-emerald-100 rounded-md transition-colors cursor-pointer"
          >
            <HiXMark className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Quick Prompts on initial conversation */}
      {messages.length <= 1 && (
        <div className="px-4 sm:px-6 pt-4 pb-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-stone-500 uppercase tracking-wider mb-2">
            <HiSparkles className="w-4 h-4 text-accent-600" />
            <span>Suggested Inquiries</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {QUICK_QUESTIONS.map((q, idx) => (
              <button
                key={idx}
                type="button"
                disabled={isLoading}
                onClick={() => sendMessage(q.text)}
                className="text-left p-2.5 bg-white hover:bg-stone-50 hover:border-primary-300 border border-stone-200 rounded-xl text-xs text-stone-700 transition-all shadow-2xs group cursor-pointer flex items-center justify-between gap-2"
              >
                <span className="font-medium group-hover:text-primary-900 transition-colors">
                  {q.text}
                </span>
                <span className="text-[10px] bg-stone-100 text-stone-500 px-1.5 py-0.5 rounded font-mono shrink-0">
                  {q.tag}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages Scroll Area */}
      <MessageList />

      {/* Input Area */}
      <div className="p-3 sm:p-4 bg-white/90 border-t border-stone-200/80">
        <MessageInput />
      </div>
    </div>
  );
};

export default ChatInterface;
