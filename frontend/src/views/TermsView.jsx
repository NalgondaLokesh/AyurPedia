import React from 'react';
import { HiDocumentText } from 'react-icons/hi2';

export const TermsView = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-3xl p-8 border border-stone-200 shadow-glass space-y-6">
        <div className="flex items-center gap-3 border-b border-stone-200 pb-4">
          <div className="p-2.5 bg-primary-100 text-primary-800 rounded-2xl">
            <HiDocumentText className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-stone-900">Terms of Use</h1>
            <p className="text-xs text-stone-500">AyurPedia Platform Terms & Conditions</p>
          </div>
        </div>

        <div className="space-y-4 text-xs sm:text-sm text-stone-700 leading-relaxed">
          <p>
            By accessing or using the AyurPedia platform, you agree to comply with the terms governing our AI-assisted regulatory analysis system.
          </p>
          <h2 className="text-base font-bold text-stone-900 pt-2">1. Permitted Use</h2>
          <p>
            AyurPedia is intended for legal research, formulation regulatory categorization, and educational compliance guidance regarding Ayurvedic intellectual property and traditional knowledge.
          </p>
          <h2 className="text-base font-bold text-stone-900 pt-2">2. Limitation of Liability</h2>
          <p>
            AyurPedia and its developers shall not be held liable for commercial decisions, patent filing rejections, or licensing disputes arising from Reliance on AI outputs.
          </p>
        </div>
      </div>
    </div>
  );
};

export default TermsView;
