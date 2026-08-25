import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatContext } from '../../context/ChatContext';
import { useApp } from '../../context/AppContext';
import ConfidenceBadge from '../Common/ConfidenceBadge';
import { HiSparkles, HiChatBubbleLeftRight, HiArrowPath, HiScale, HiCheckCircle, HiUserGroup } from 'react-icons/hi2';
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
    navigate('/');
    
    // Automatically trigger an initial legal inquiry prompt in chat
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

  return (
    <div className="space-y-6 animate-in fade-in zoom-in-95 duration-200">
      {/* Result Top Card */}
      <div className="p-6 bg-gradient-to-br from-primary-900 via-primary-800 to-emerald-950 text-white rounded-3xl shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
          <HiScale className="w-36 h-36" />
        </div>

        <div className="relative z-10">
          <div className="flex items-center justify-between gap-3 mb-3 flex-wrap">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider bg-white/20 text-accent-100 rounded-lg backdrop-blur-xs">
                Classification Complete
              </span>
              <span className="px-2.5 py-1 text-[11px] font-semibold bg-emerald-700/60 text-emerald-100 rounded-lg">
                Jurisdiction: {jurisdiction}
              </span>
            </div>

            <ConfidenceBadge
              confidence={confidence >= 0.8 ? 'High' : confidence >= 0.5 ? 'Medium' : 'Low'}
              score={confidence}
            />
          </div>

          <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white mb-2">
            {category}
          </h2>

          <p className="text-xs sm:text-sm text-emerald-100 leading-relaxed max-w-2xl">
            {description}
          </p>

          {/* Confidence Progress */}
          <div className="mt-4 pt-4 border-t border-white/15 max-w-md">
            <div className="flex justify-between text-xs text-emerald-200 font-bold mb-1">
              <span>Regulatory Categorization Confidence</span>
              <span className="font-mono">{Math.round(confidence * 100)}%</span>
            </div>
            <div className="w-full bg-white/20 h-2 rounded-full overflow-hidden">
              <div
                className="bg-accent-400 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.round(confidence * 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Relevant Statutory Laws */}
      <div className="p-5 bg-white rounded-2xl border border-stone-200 shadow-2xs">
        <div className="flex items-center gap-2 text-xs font-bold text-stone-700 uppercase tracking-wider mb-3">
          <HiScale className="w-4 h-4 text-primary-700" />
          <span>Applicable Statutory Frameworks & Regulatory Acts</span>
        </div>

        {relevant_laws && relevant_laws.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {relevant_laws.map((law, idx) => (
              <div
                key={idx}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-stone-50 border border-stone-200 text-stone-800 text-xs font-semibold rounded-xl"
              >
                <HiCheckCircle className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>{law}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-stone-500">
            Standard Drugs & Cosmetics Act 1940 and Patents Act 1970 apply.
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button
            type="button"
            onClick={onReset}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-4 py-2.5 text-xs font-semibold text-stone-700 bg-white hover:bg-stone-50 border border-stone-200 rounded-xl transition-all cursor-pointer"
          >
            <HiArrowPath className="w-4 h-4" />
            <span>Classify Another</span>
          </button>

          <button
            type="button"
            onClick={handleCopyResult}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-4 py-2.5 text-xs font-semibold text-stone-700 bg-white hover:bg-stone-50 border border-stone-200 rounded-xl transition-all cursor-pointer"
          >
            <span>Copy Summary</span>
          </button>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button
            type="button"
            onClick={() => openFacilitatorModal({ ...result })}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-4 py-2.5 text-xs font-semibold text-primary-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-xl transition-all cursor-pointer"
          >
            <HiUserGroup className="w-4 h-4 text-primary-700" />
            <span>Ask Facilitator</span>
          </button>

          <button
            type="button"
            onClick={handleUseInChat}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-2 px-5 py-2.5 text-xs font-bold text-white bg-primary-700 hover:bg-primary-800 active:scale-95 rounded-xl shadow-md transition-all cursor-pointer"
          >
            <HiChatBubbleLeftRight className="w-4 h-4" />
            <span>Use in Legal Chat</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClassificationResult;
