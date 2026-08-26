import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatContext } from '../../context/ChatContext';
import { useApp } from '../../context/AppContext';
import ConfidenceBadge from '../Common/ConfidenceBadge';
import { Mandala } from '../Common/Botanical';
import { HiChatBubbleLeftRight, HiArrowPath, HiScale, HiCheckCircle, HiUserGroup, HiClipboard } from 'react-icons/hi2';
import toast from 'react-hot-toast';

export const ClassificationResult = ({ result, onReset }) => {
  const navigate = useNavigate();
  const { attachClassification, sendMessage } = useChatContext();
  const { setActiveTab, openFacilitatorModal } = useApp();

  if (!result) return null;

  const {
    category = 'Proprietary',
    confidence = 0.85,
    relevant_laws = [],
    description = 'No detailed description available.',
    jurisdiction = 'India',
  } = result;

  const handleUseInChat = () => {
    attachClassification(result);
    setActiveTab('chat');
    navigate('/chat');

    setTimeout(() => {
      sendMessage(`What are the patentability and licensing guidelines for my ${category} formulation under ${jurisdiction} law?`);
    }, 150);
  };

  const handleCopyResult = () => {
    const text = `AyurPedia Classification:
Category: ${category}
Confidence: ${Math.round(confidence * 100)}%
Relevant Laws: ${relevant_laws.join(', ')}
Description: ${description}`;
    navigator.clipboard.writeText(text);
    toast.success('Classification summary copied to clipboard');
  };

  const pct = Math.round(confidence * 100);

  return (
    <div className="space-y-6 scale-in">
      {/* Result Top Card */}
      <div className="p-6 sm:p-7 bg-primary-900 text-white rounded-3xl shadow-card relative overflow-hidden">
        <Mandala className="absolute -top-14 -right-14 w-56 h-56 text-accent-400/10 pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center justify-between gap-3 mb-3 flex-wrap">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 text-[11px] font-bold uppercase tracking-[0.12em] bg-accent-500/20 text-accent-200 rounded-lg border border-accent-400/30">
                Classification Complete
              </span>
              <span className="px-2.5 py-1 text-[11px] font-semibold bg-primary-700/60 text-stone-200 rounded-lg">
                Jurisdiction: {jurisdiction}
              </span>
            </div>

            <ConfidenceBadge
              confidence={confidence >= 0.8 ? 'High' : confidence >= 0.5 ? 'Medium' : 'Low'}
              score={confidence}
            />
          </div>

          <h2 className="text-2xl sm:text-3xl font-serif font-semibold tracking-tight text-white mb-2">
            {category}
          </h2>

          <p className="text-xs sm:text-sm text-stone-300 leading-relaxed max-w-2xl">
            {description}
          </p>

          {/* Confidence Progress */}
          <div className="mt-5 pt-5 border-t border-white/10 max-w-md">
            <div className="flex justify-between text-xs text-stone-300 font-semibold mb-1.5">
              <span>Regulatory Categorization Confidence</span>
              <span className="font-mono text-accent-300">{pct}%</span>
            </div>
            <div className="w-full bg-white/15 h-2 rounded-full overflow-hidden">
              <div
                className="bg-accent-400 h-full rounded-full transition-all duration-700 ease-out"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Relevant Statutory Laws */}
      <div className="p-5 bg-[#fffdf8] dark:bg-primary-950/40 rounded-2xl border border-stone-200/80 dark:border-primary-900/50 shadow-subtle">
        <div className="flex items-center gap-2 text-[11px] font-bold text-stone-600 dark:text-stone-400 uppercase tracking-[0.12em] mb-3">
          <HiScale className="w-4 h-4 text-primary-700 dark:text-accent-400" />
          <span>Applicable Statutory Frameworks &amp; Regulatory Acts</span>
        </div>

        {relevant_laws && relevant_laws.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {relevant_laws.map((law, idx) => (
              <div
                key={idx}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-stone-50 dark:bg-primary-900/40 border border-stone-200 dark:border-primary-900/50 text-stone-800 dark:text-stone-200 text-xs font-semibold rounded-xl transition-all duration-200 hover:border-accent-300 hover:bg-accent-50 dark:hover:bg-primary-900/60 cursor-default"
              >
                <HiCheckCircle className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                <span>{law}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-stone-500 dark:text-stone-400">
            Standard Drugs &amp; Cosmetics Act 1940 and Patents Act 1970 apply.
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button
            type="button"
            onClick={onReset}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-4 py-2.5 text-xs font-semibold text-stone-700 dark:text-stone-300 bg-white dark:bg-primary-950/50 hover:bg-stone-50 dark:hover:bg-primary-900/50 border border-stone-200 dark:border-primary-900/50 rounded-xl transition-all duration-200 cursor-pointer focus-ring"
          >
            <HiArrowPath className="w-4 h-4" />
            <span>Classify Another</span>
          </button>

          <button
            type="button"
            onClick={handleCopyResult}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-4 py-2.5 text-xs font-semibold text-stone-700 dark:text-stone-300 bg-white dark:bg-primary-950/50 hover:bg-stone-50 dark:hover:bg-primary-900/50 border border-stone-200 dark:border-primary-900/50 rounded-xl transition-all duration-200 cursor-pointer focus-ring"
          >
            <HiClipboard className="w-4 h-4" />
            <span>Copy Summary</span>
          </button>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button
            type="button"
            onClick={() => openFacilitatorModal({ ...result })}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-4 py-2.5 text-xs font-semibold text-primary-800 dark:text-accent-200 bg-accent-50 dark:bg-accent-500/15 hover:bg-accent-100 dark:hover:bg-accent-500/25 border border-accent-200 dark:border-accent-500/30 rounded-xl transition-all duration-200 cursor-pointer focus-ring"
          >
            <HiUserGroup className="w-4 h-4" />
            <span>Ask Facilitator</span>
          </button>

          <button
            type="button"
            onClick={handleUseInChat}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-2 px-5 py-2.5 text-xs font-bold text-white btn-premium rounded-xl transition-all duration-200 cursor-pointer"
          >
            <HiChatBubbleLeftRight className="w-4 h-4 text-accent-300" />
            <span>Use in Legal Chat</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClassificationResult;
