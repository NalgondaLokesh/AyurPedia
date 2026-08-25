import React from 'react';
import { HiShieldExclamation, HiUserGroup } from 'react-icons/hi2';
import { useApp } from '../../context/AppContext';

export const Disclaimer = ({ compact = false, showEscalation = true }) => {
  const { openFacilitatorModal } = useApp();

  if (compact) {
    return (
      <div className="flex items-center justify-between gap-2 p-2 bg-amber-50/80 border border-amber-200/80 rounded-lg text-xs text-amber-900">
        <div className="flex items-center gap-1.5 font-medium">
          <HiShieldExclamation className="w-4 h-4 text-amber-600 shrink-0" />
          <span>⚠️ <strong>Disclaimer:</strong> This is regulatory information, not legal advice.</span>
        </div>
        {showEscalation && (
          <button
            type="button"
            onClick={() => openFacilitatorModal()}
            className="text-primary-700 hover:text-primary-900 font-semibold underline shrink-0 cursor-pointer"
          >
            Ask Facilitator
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="p-3.5 bg-gradient-to-r from-amber-50/90 via-stone-50 to-amber-50/90 border border-amber-200/90 rounded-2xl shadow-2xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-start gap-2.5">
          <div className="p-1.5 bg-amber-100 rounded-lg text-amber-700 shrink-0 mt-0.5 sm:mt-0">
            <HiShieldExclamation className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-amber-950 uppercase tracking-wider">
              Legal Disclaimer & Guidance
            </h4>
            <p className="text-xs text-amber-900 mt-0.5 leading-relaxed">
              AyurPedia provides AI-assisted intelligence on Indian and International traditional knowledge frameworks (Patents Act 1970, BD Act 2002, FSSAI, WIPO GRATK). Information generated does not constitute formal legal counsel or patent filing certification.
            </p>
          </div>
        </div>

        {showEscalation && (
          <button
            type="button"
            onClick={() => openFacilitatorModal()}
            className="inline-flex items-center justify-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-white bg-primary-700 hover:bg-primary-800 active:scale-95 rounded-xl shadow-xs transition-all shrink-0 cursor-pointer"
          >
            <HiUserGroup className="w-4 h-4" />
            <span>Connect Facilitator</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default Disclaimer;
