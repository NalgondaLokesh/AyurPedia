import React from 'react';
import { HiDocumentText } from 'react-icons/hi2';

export const TermsView = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="bg-[#fffdf8] dark:bg-primary-950/40 rounded-3xl p-8 border border-stone-200/80 dark:border-primary-900/50 shadow-card space-y-6">
        <div className="flex items-center gap-3 border-b border-stone-200 dark:border-primary-900/50 pb-5">
          <div className="p-2.5 bg-primary-100 dark:bg-primary-500/15 text-primary-700 dark:text-primary-300 rounded-2xl">
            <HiDocumentText className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-serif font-semibold text-stone-900 dark:text-stone-100">Terms of Use</h1>
            <p className="text-xs text-stone-500 dark:text-stone-400 mt-0.5">AyurPedia Platform Terms &amp; Conditions</p>
          </div>
        </div>

        <div className="space-y-5 text-sm text-stone-700 dark:text-stone-300 leading-relaxed">
          <p>
            By accessing or using the AyurPedia platform, you agree to comply with the terms governing our AI-assisted regulatory analysis system.
          </p>
          <section className="space-y-1.5">
            <h2 className="text-base font-serif font-semibold text-stone-900 dark:text-stone-100">1. Permitted Use</h2>
            <p>
              AyurPedia is intended for legal research, formulation regulatory categorization, and educational compliance guidance regarding Ayurvedic intellectual property and traditional knowledge.
            </p>
          </section>
          <section className="space-y-1.5">
            <h2 className="text-base font-serif font-semibold text-stone-900 dark:text-stone-100">2. Limitation of Liability</h2>
            <p>
              AyurPedia and its developers shall not be held liable for commercial decisions, patent filing rejections, or licensing disputes arising from reliance on AI outputs.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default TermsView;
