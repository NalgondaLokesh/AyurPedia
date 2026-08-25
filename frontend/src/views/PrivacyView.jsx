import React from 'react';
import { HiShieldCheck } from 'react-icons/hi2';

export const PrivacyView = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-3xl p-8 border border-stone-200 shadow-glass space-y-6">
        <div className="flex items-center gap-3 border-b border-stone-200 pb-4">
          <div className="p-2.5 bg-emerald-100 text-emerald-800 rounded-2xl">
            <HiShieldCheck className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-stone-900">Privacy Policy</h1>
            <p className="text-xs text-stone-500">AyurPedia Data Protection & Formulation Confidentiality</p>
          </div>
        </div>

        <div className="space-y-4 text-xs sm:text-sm text-stone-700 leading-relaxed">
          <p>
            At AyurPedia, we respect the sensitivity of herbal proprietary research, indigenous formulations, and patent discovery queries.
          </p>
          <h2 className="text-base font-bold text-stone-900 pt-2">1. Data Storage</h2>
          <p>
            Chat messages and formulation inputs are processed locally in session memory and routed securely to the RAG backend. No formulation recipe is sold or shared with third-party advertisers.
          </p>
          <h2 className="text-base font-bold text-stone-900 pt-2">2. Multilingual Translation via Bhashini</h2>
          <p>
            When utilizing Indian language translation via government Bhashini APIs, data transmissions occur over encrypted TLS protocols strictly for natural language inference.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PrivacyView;
