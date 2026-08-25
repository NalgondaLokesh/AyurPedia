import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { useChatContext } from '../../context/ChatContext';
import CitationCard from './CitationCard';
import ConfidenceBadge from '../Common/ConfidenceBadge';
import Disclaimer from '../Common/Disclaimer';
import { HiUser, HiSparkles, HiBookmark } from 'react-icons/hi2';

export const MessageList = () => {
  const { messages, isLoading } = useChatContext();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
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
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-primary-800 to-herbal-leaf text-white flex items-center justify-center shrink-0 shadow-xs mt-1">
                <span className="font-serif font-bold text-xs">A</span>
              </div>
            )}

            {/* Message Bubble */}
            <div
              className={`max-w-3xl rounded-2xl p-4 sm:p-5 shadow-2xs ${
                isUser
                  ? 'bg-primary-700 text-white rounded-tr-xs'
                  : message.isError
                  ? 'bg-rose-50/90 border border-rose-200 text-rose-950 rounded-tl-xs'
                  : 'bg-white/95 border border-stone-200/80 text-stone-800 rounded-tl-xs'
              }`}
            >
              {/* Message Header (for Assistant) */}
              {!isUser && (
                <div className="flex items-center justify-between gap-2 pb-2.5 mb-3 border-b border-stone-100 flex-wrap">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs text-primary-950">AyurPedia Legal AI</span>
                    {message.jurisdiction && (
                      <span className="px-2 py-0.5 text-[10px] font-semibold bg-stone-100 text-stone-600 rounded-md">
                        {message.jurisdiction}
                      </span>
                    )}
                  </div>

                  {message.confidence && (
                    <ConfidenceBadge confidence={message.confidence} />
                  )}
                </div>
              )}

              {/* Message Content */}
              <div className={`prose-ayurpedia ${isUser ? 'text-white' : 'text-stone-800'}`}>
                {isUser ? (
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.text}</p>
                ) : (
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                )}
              </div>

              {/* Citations section if available */}
              {!isUser && message.citations && message.citations.length > 0 && (
                <div className="mt-4 pt-3.5 border-t border-stone-100">
                  <div className="flex items-center gap-1.5 mb-2.5 text-xs font-bold text-stone-700 uppercase tracking-wider">
                    <HiBookmark className="w-4 h-4 text-emerald-700" />
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

              {/* Timestamp */}
              <div
                className={`mt-2 text-[10px] ${
                  isUser ? 'text-primary-100 text-right' : 'text-stone-400 text-left'
                }`}
              >
                {new Date(message.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </div>
            </div>

            {/* User Avatar */}
            {isUser && (
              <div className="w-8 h-8 rounded-xl bg-stone-200 text-stone-700 flex items-center justify-center shrink-0 shadow-xs mt-1">
                <HiUser className="w-4 h-4" />
              </div>
            )}
          </div>
        );
      })}

      {/* Loading Indicator */}
      {isLoading && (
        <div className="flex items-start gap-3 fade-in justify-start">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-primary-800 to-herbal-leaf text-white flex items-center justify-center shrink-0 shadow-xs mt-1 animate-pulse">
            <span className="font-serif font-bold text-xs">A</span>
          </div>
          <div className="bg-white/95 border border-stone-200 rounded-2xl rounded-tl-xs p-4 shadow-2xs flex items-center gap-3">
            <div className="flex space-x-1.5">
              <div className="w-2.5 h-2.5 bg-primary-600 rounded-full animate-bounce"></div>
              <div className="w-2.5 h-2.5 bg-primary-500 rounded-full animate-bounce [animation-delay:0.2s]"></div>
              <div className="w-2.5 h-2.5 bg-herbal-leaf rounded-full animate-bounce [animation-delay:0.4s]"></div>
            </div>
            <span className="text-xs text-stone-500 font-medium">
              Retrieving legal documents & formulating cited response...
            </span>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
