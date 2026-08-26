import React, { useState } from 'react';
import { HiDocumentText, HiClipboardDocumentCheck, HiClipboard, HiCheckBadge, HiArrowTopRightOnSquare, HiChevronDown } from 'react-icons/hi2';
import toast from 'react-hot-toast';

export const CitationCard = ({ citation, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const { source = 'Legal Document', section = '', text = '', url = null } = citation;

  const handleCopy = (e) => {
    e.stopPropagation();
    const citationString = `[Source: ${source}, Section: ${section}]`;
    navigator.clipboard.writeText(text || citationString);
    setCopied(true);
    toast.success('Citation copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white dark:bg-primary-950/40 border border-stone-200/90 dark:border-primary-900/50 rounded-xl p-3 shadow-subtle hover:border-accent-300/70 transition-all duration-300 text-xs cursor-default">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2 min-w-0">
          <div className="p-1.5 bg-emerald-50 dark:bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 rounded-lg shrink-0 mt-0.5">
            <HiDocumentText className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="font-bold text-stone-900 dark:text-stone-100 truncate">
                [{index + 1}] {source}
              </span>
              <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-emerald-50 dark:bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 font-semibold text-[10px] rounded-md border border-emerald-200 dark:border-emerald-500/30">
                <HiCheckBadge className="w-3 h-3" />
                <span>Verified</span>
              </span>
            </div>
            {section && (
              <p className="text-stone-600 dark:text-stone-400 font-medium text-[11px] mt-0.5">
                Section / Rule: <span className="text-primary-800 dark:text-accent-300 font-mono">{section}</span>
              </p>
            )}
          </div>
        </div>

        {/* Copy and link actions */}
        <div className="flex items-center gap-1 shrink-0">
          <button
            type="button"
            onClick={handleCopy}
            title="Copy citation"
            className="p-1.5 text-stone-500 hover:text-stone-800 dark:text-stone-400 dark:hover:text-stone-200 hover:bg-stone-100 dark:hover:bg-primary-900/40 rounded-lg transition-all duration-200 cursor-pointer focus-ring"
          >
            {copied ? (
              <HiClipboardDocumentCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            ) : (
              <HiClipboard className="w-4 h-4" />
            )}
          </button>

          {url && (
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              title="Open authoritative source document"
              className="p-1.5 text-stone-500 hover:text-primary-700 dark:text-stone-400 dark:hover:text-accent-300 hover:bg-stone-100 dark:hover:bg-primary-900/40 rounded-lg transition-all duration-200 focus-ring"
            >
              <HiArrowTopRightOnSquare className="w-4 h-4" />
            </a>
          )}
        </div>
      </div>

      {/* Expandable text snippet if present */}
      {text && text !== `${source}, ${section}` && (
        <div className="mt-2 pt-2 border-t border-stone-100 dark:border-primary-900/50">
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center justify-between w-full text-[11px] font-medium text-stone-500 dark:text-stone-400 hover:text-stone-800 dark:hover:text-stone-200 transition-colors"
          >
            <span>{isExpanded ? 'Hide context snippet' : 'View context snippet'}</span>
            <HiChevronDown className={`w-3.5 h-3.5 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`} />
          </button>

          {isExpanded && (
            <p className="mt-1.5 p-2 bg-stone-50 dark:bg-primary-900/40 rounded-lg text-stone-700 dark:text-stone-300 leading-relaxed font-sans text-[11px] border border-stone-200/50 dark:border-primary-900/50 fade-in">
              "{text}"
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default CitationCard;
