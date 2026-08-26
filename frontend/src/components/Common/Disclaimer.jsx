import React from 'react';
import { HiShieldExclamation, HiUserGroup } from 'react-icons/hi2';
import { useApp } from '../../context/AppContext';

export const Disclaimer = ({ compact = false, showEscalation = true }) => {
  const { openFacilitatorModal } = useApp();

  if (compact) {
    return (
      <div className="flex items-center justify-between gap-2 p-2.5 bg-accent-50/80 dark:bg-accent-500/10 border border-accent-200/70 dark:border-accent-500/25 rounded-lg text-xs text-stone-700 dark:text-stone-300">
        <div className="flex items-center gap-1.5 font-medium">
          <HiShieldExclamation className="w-4 h-4 text-accent-600 dark:text-accent-400 shrink-0" />
          <span><strong className="text-stone-800 dark:text-stone-100">Disclaimer:</strong> This is regulatory information, not legal advice.</span>
        </div>
        {showEscalation && (
          <button
            type="button"
            onClick={() => openFacilitatorModal()}
            className="text-primary-700 dark:text-accent-300 hover:text-primary-900 dark:hover:text-accent-200 font-semibold underline shrink-0 cursor-pointer"
          >
            Ask Facilitator
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="p-4 bg-accent-50/70 dark:bg-accent-500/10 border border-accent-200/70 dark:border-accent-500/25 rounded-2xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-start gap-2.5">
          <div className="p-1.5 bg-accent-100 dark:bg-accent-500/20 rounded-lg text-accent-700 dark:text-accent-300 shrink-0 mt-0.5 sm:mt-0">
            <HiShieldExclamation className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-[11px] font-bold text-stone-800 dark:text-stone-200 uppercase tracking-[0.12em]">
              Legal Disclaimer &amp; Guidance
            </h4>
            <p className="text-xs text-stone-600 dark:text-stone-400 mt-0.5 leading-relaxed">
              AyurPedia provides AI-assisted intelligence on Indian and International traditional knowledge frameworks (Patents Act 1970, BD Act 2002, FSSAI, WIPO GRATK). Information generated does not constitute formal legal counsel or patent filing certification.
            </p>
          </div>
        </div>

        {showEscalation && (
          <button
            type="button"
            onClick={() => openFacilitatorModal()}
            className="inline-flex items-center justify-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-white btn-premium rounded-xl transition-all shrink-0 cursor-pointer"
          >
            <HiUserGroup className="w-4 h-4 text-accent-300" />
            <span>Connect Facilitator</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default Disclaimer;
