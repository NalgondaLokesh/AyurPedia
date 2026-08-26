import React from 'react';
import { HiShieldCheck } from 'react-icons/hi2';

export const PrivacyView = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="bg-[#fffdf8] dark:bg-primary-950/40 rounded-3xl p-8 border border-stone-200/80 dark:border-primary-900/50 shadow-card space-y-6">
        <div className="flex items-center gap-3 border-b border-stone-200 dark:border-primary-900/50 pb-5">
          <div className="p-2.5 bg-emerald-100 dark:bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 rounded-2xl">
            <HiShieldCheck className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-serif font-semibold text-stone-900 dark:text-stone-100">Privacy Policy</h1>
            <p className="text-xs text-stone-500 dark:text-stone-400 mt-0.5">AyurPedia Data Protection &amp; Formulation Confidentiality</p>
          </div>
        </div>

        <div className="space-y-5 text-sm text-stone-700 dark:text-stone-300 leading-relaxed">
          <p>
            At AyurPedia, we respect the sensitivity of herbal proprietary research, indigenous formulations, and patent discovery queries.
          </p>
          <section className="space-y-1.5">
            <h2 className="text-base font-serif font-semibold text-stone-900 dark:text-stone-100">1. Data Storage</h2>
            <p>
              Chat messages and formulation inputs are processed in session memory and routed securely to the RAG backend. No formulation recipe is sold or shared with third-party advertisers.
            </p>
          </section>
          <section className="space-y-1.5">
            <h2 className="text-base font-serif font-semibold text-stone-900 dark:text-stone-100">2. Multilingual Translation via Bhashini</h2>
            <p>
              When utilizing Indian language translation via government Bhashini APIs, data transmissions occur over encrypted TLS protocols strictly for natural language inference.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default PrivacyView;
