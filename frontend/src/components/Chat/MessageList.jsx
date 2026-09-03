import React, { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useChatContext } from '../../context/ChatContext';
import CitationCard from './CitationCard';
import ConfidenceBadge from '../Common/ConfidenceBadge';
import Disclaimer from '../Common/Disclaimer';
import { AyurMark } from '../Common/Botanical';
import { HiUser, HiBookmark, HiHandThumbUp, HiHandThumbDown } from 'react-icons/hi2';

export const MessageList = () => {
  const { messages, isLoading } = useChatContext();
  const messagesEndRef = useRef(null);
  const [feedback, setFeedback] = useState({});

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleFeedback = (messageId, type) => {
    setFeedback(prev => ({
      ...prev,
      [messageId]: type
    }));
    // In production, send feedback to backend
    console.log(`Feedback ${type} for message ${messageId}`);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-2 sm:px-4 py-4 space-y-6">
      {messages.map((message) => {
        const isUser = message.sender === 'user';

        return (
          <div
            key={message.id}
            className={`flex items-start gap-3 fade-in ${
              isUser ? 'justify-end' : 'justify-start'
            }`}
          >
            {/* Assistant Avatar */}
            {!isUser && (
              <div className="w-9 h-9 rounded-xl bg-primary-800 text-accent-300 ring-1 ring-primary-700/40 flex items-center justify-center shrink-0 shadow-subtle mt-1">
                <AyurMark className="w-5 h-5" />
              </div>
            )}

            {/* Message Bubble */}
            <div
              className={`max-w-3xl min-w-0 break-words rounded-2xl p-4 sm:p-5 transition-all duration-300 ${
                isUser
                  ? 'bg-primary-800 text-stone-50 rounded-tr-sm shadow-card'
                  : message.isError
                  ? 'bg-clay-50 border border-clay-200 text-clay-900 rounded-tl-sm'
                  : 'bg-[#fffdf8] dark:bg-primary-950/40 border border-stone-200/80 dark:border-primary-900/50 text-stone-800 dark:text-stone-200 rounded-tl-sm shadow-subtle hover:border-accent-300/60'
              }`}
            >
              {/* Message Header (for Assistant) */}
              {!isUser && (
                <div className="flex items-center justify-between gap-2 pb-2.5 mb-3 border-b border-stone-100 dark:border-primary-900/50 flex-wrap">
                  <div className="flex items-center gap-2">
                    <span className="font-serif font-semibold text-sm text-primary-800 dark:text-accent-200">AyurPedia Legal AI</span>
                    {message.jurisdiction && (
                      <span className="px-2 py-0.5 text-[10px] font-semibold bg-stone-100 dark:bg-primary-900/50 text-stone-600 dark:text-stone-400 rounded-md">
                        {message.jurisdiction}
                      </span>
                    )}
                  </div>

                  {message.confidence && (
                    <ConfidenceBadge confidence={message.confidence} score={message.confidence_score} />
                  )}
                </div>
              )}

              {/* Message Content */}
              <div className={`prose-ayurpedia ${isUser ? 'text-stone-50' : 'text-stone-800 dark:text-stone-200'}`}>
                {isUser ? (
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.text}</p>
                ) : (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>
                )}
              </div>

              {/* Citations section if available */}
              {!isUser && message.citations && message.citations.length > 0 && (
                <div className="mt-4 pt-3.5 border-t border-stone-100 dark:border-primary-900/50">
                  <div className="flex items-center gap-1.5 mb-2.5 text-[11px] font-bold text-stone-600 dark:text-stone-400 uppercase tracking-[0.12em]">
                    <HiBookmark className="w-4 h-4 text-accent-600 dark:text-accent-400" />
                    <span>Authoritative Citations ({message.citations.length})</span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {message.citations.map((citation, idx) => (
                      <CitationCard key={idx} citation={citation} index={idx} />
                    ))}
                  </div>
                </div>
              )}

              {/* Compact Disclaimer on Assistant messages */}
              {!isUser && !message.isError && (
                <div className="mt-4 pt-2">
                  <Disclaimer compact={true} showEscalation={true} />
                </div>
              )}

              {/* Timestamp & Feedback */}
              <div
                className={`mt-2 flex items-center gap-3 ${
                  isUser ? 'text-stone-300 justify-end' : 'text-stone-400 justify-between'
                }`}
              >
                <div className="text-[10px]">
                  {new Date(message.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>
                
                {/* Feedback Buttons (Assistant only) */}
                {!isUser && (
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => handleFeedback(message.id, 'up')}
                      className={`p-1.5 rounded-lg transition-all ${
                        feedback[message.id] === 'up'
                          ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300'
                          : 'hover:bg-stone-100 dark:hover:bg-primary-900/40 text-stone-400 hover:text-stone-600 dark:hover:text-stone-300'
                      }`}
                      title="Helpful"
                    >
                      <HiHandThumbUp className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleFeedback(message.id, 'down')}
                      className={`p-1.5 rounded-lg transition-all ${
                        feedback[message.id] === 'down'
                          ? 'bg-clay-100 text-clay-600 dark:bg-clay-900/30 dark:text-clay-300'
                          : 'hover:bg-stone-100 dark:hover:bg-primary-900/40 text-stone-400 hover:text-stone-600 dark:hover:text-stone-300'
                      }`}
                      title="Not helpful"
                    >
                      <HiHandThumbDown className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* User Avatar */}
            {isUser && (
              <div className="w-9 h-9 rounded-xl bg-stone-200 dark:bg-primary-900/60 text-stone-600 dark:text-stone-300 flex items-center justify-center shrink-0 shadow-subtle mt-1">
                <HiUser className="w-4 h-4" />
              </div>
            )}
          </div>
        );
      })}

      {/* Loading Indicator */}
      {isLoading && (
        <div className="flex items-start gap-3 fade-in justify-start">
          <div className="w-9 h-9 rounded-xl bg-primary-800 text-accent-300 ring-1 ring-primary-700/40 flex items-center justify-center shrink-0 shadow-subtle mt-1 animate-pulse">
            <AyurMark className="w-5 h-5" />
          </div>
          <div className="bg-[#fffdf8] dark:bg-primary-950/40 border border-stone-200/80 dark:border-primary-900/50 rounded-2xl rounded-tl-sm p-4 shadow-subtle flex items-center gap-3">
            <div className="flex space-x-1.5">
              <div className="w-2.5 h-2.5 bg-primary-700 rounded-full loading-dot"></div>
              <div className="w-2.5 h-2.5 bg-primary-500 rounded-full loading-dot"></div>
              <div className="w-2.5 h-2.5 bg-accent-500 rounded-full loading-dot"></div>
            </div>
            <span className="text-xs text-stone-500 dark:text-stone-400 font-medium">
              Retrieving legal documents &amp; formulating cited response&hellip;
            </span>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
