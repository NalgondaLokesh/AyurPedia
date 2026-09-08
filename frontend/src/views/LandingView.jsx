import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  HiDocumentMagnifyingGlass, HiChatBubbleLeftRight, HiArrowRight,
  HiGlobeAmericas, HiScale, HiBookOpen, HiCheckCircle, HiSparkles
} from 'react-icons/hi2';
import { AyurMark } from '../components/Common/Botanical';

export const LandingView = () => {
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const FEATURES = [
    {
      title: 'Formulation Classification',
      description: 'Categorise herbal products across 7 statutory classes with grounded AI analysis.',
      stat: '7 Classes'
    },
    {
      title: 'Legal Intelligence Chat',
      description: 'Interactive Q&A with verified statutory citations and calibrated confidence scoring.',
      stat: '95% Accuracy'
    },
    {
      title: 'Citation Enforcement',
      description: 'Every answer is backed by authoritative legal documents — never unsupported claims.',
      stat: '100% Sourced'
    },
    {
      title: 'Multilingual Support',
      description: '10+ Indian languages with real-time translation, so guidance meets you in your tongue.',
      stat: '10+ Languages'
    },
    {
      title: 'Jurisdiction Toggle',
      description: 'Move seamlessly between Indian and International legal frameworks in a single click.',
      stat: '2 Frameworks'
    },
    {
      title: 'Ayurveda-Focused',
      description: 'Purpose-built for Ayurvedic IPR, TKDL prior art, and Traditional Knowledge compliance.',
      stat: 'TKDL Ready'
    },
  ];

  const FRAMEWORKS = [
    'Patents Act 1970', 'Biological Diversity Act 2002', 'FSSAI Ayurveda-Aahar',
    'WIPO GRATK 2024', 'TRIPS Agreement', 'Nagoya Protocol', 'CBD',
  ];

  return (
    <div className="relative min-h-screen bg-stone-50 dark:bg-[#0a1310]">
      {/* ================= HERO SECTION ================= */}
      <section className="relative overflow-hidden">
        {/* Subtle grid background */}
        <div className="absolute inset-0 ledger-grid opacity-40" aria-hidden="true" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-20 sm:pt-36 sm:pb-28">
          <div className="flex items-start justify-between gap-12">
            {/* Left content */}
            <div className="flex-1 max-w-2xl">
              {/* Editorial rule label */}
              <div className="flex items-center gap-3 mb-10 reveal is-visible">
                <div className="rule-label">
                  <span>Legal Intelligence Platform</span>
                </div>
                <span className="micro-mono text-stone-400 dark:text-stone-500">v2.0</span>
              </div>

              {/* Main headline */}
              <h1 className="font-serif text-5xl sm:text-6xl lg:text-7xl font-semibold text-stone-900 dark:text-stone-50 mb-8 leading-[1.1] reveal reveal-delay-1 is-visible">
                Ayurvedic IPR,<br />
                <span className="text-primary-800 dark:text-accent-300">grounded in law.</span>
              </h1>

              {/* Subheadline */}
              <p className="text-xl sm:text-2xl text-stone-600 dark:text-stone-400 mb-12 leading-relaxed reveal reveal-delay-2 is-visible">
                Navigate the intersection of traditional knowledge and intellectual property with 
                citation-backed guidance across Indian and international frameworks.
              </p>

              {/* Primary CTAs */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 mb-20 reveal reveal-delay-1 is-visible">
                <button
                  onClick={() => navigate('/chat')}
                  className="group inline-flex items-center justify-center gap-2 w-full sm:w-auto px-9 py-4 text-sm font-semibold text-white bg-primary-900 dark:bg-primary-800 hover:bg-primary-800 dark:hover:bg-primary-700 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl hover:-translate-y-0.5"
                >
                  <HiChatBubbleLeftRight className="w-5 h-5" />
                  <span>Start Legal Chat</span>
                  <HiArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                </button>
                <button
                  onClick={() => navigate('/classify')}
                  className="group inline-flex items-center justify-center gap-2 w-full sm:w-auto px-9 py-4 text-sm font-semibold text-stone-700 dark:text-stone-200 bg-white dark:bg-primary-900/40 hover:bg-stone-50 dark:hover:bg-primary-900/60 border border-stone-200 dark:border-primary-800 rounded-lg transition-all duration-200 hover:-translate-y-0.5"
                >
                  <HiDocumentMagnifyingGlass className="w-5 h-5" />
                  <span>Classify Formulation</span>
                </button>
              </div>

              {/* Frameworks rail */}
              <div className="border-y border-stone-200 dark:border-primary-800/50 py-8 reveal reveal-delay-2 is-visible">
                <div className="flex items-center gap-3 mb-5">
                  <HiBookOpen className="w-4 h-4 text-primary-700 dark:text-accent-400" />
                  <span className="text-xs font-semibold text-stone-500 dark:text-stone-400 uppercase tracking-wider">
                    Grounded in
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {FRAMEWORKS.map((framework, i) => (
                    <span
                      key={i}
                      className="cite-chip"
                    >
                      <span className="pin">{String(i + 1).padStart(2, '0')}</span>
                      {framework}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Right side - Logo */}
            <div className="hidden lg:flex items-center justify-center shrink-0 reveal reveal-delay-2 is-visible">
              <div className="relative group">
                {/* Outer glow */}
                <div className="absolute inset-0 bg-gradient-to-br from-accent-400/30 to-primary-600/30 rounded-3xl blur-xl group-hover:blur-2xl transition-all duration-500" />
                
                {/* Main logo container */}
                <div className="relative w-64 h-64 rounded-3xl bg-gradient-to-br from-primary-900 via-primary-800 to-primary-900 flex items-center justify-center text-accent-300 ring-1 ring-accent-400/30 shadow-2xl group-hover:shadow-3xl group-hover:scale-105 transition-all duration-500">
                  {/* Inner border */}
                  <span className="absolute inset-2 rounded-2xl border border-accent-400/20" />
                  
                  {/* Logo icon */}
                  <AyurMark className="w-32 h-32 relative z-10 group-hover:scale-110 transition-transform duration-500" />
                  
                  {/* Shine effect */}
                  <div className="absolute top-0 left-0 right-0 h-1/2 bg-gradient-to-b from-white/10 to-transparent rounded-t-3xl pointer-events-none" />
                </div>
                
                {/* Decorative floating elements */}
                <div className="absolute -top-6 -right-6 w-12 h-12 rounded-full bg-accent-500/20 blur-sm animate-pulse" />
                <div className="absolute -bottom-8 -left-8 w-16 h-16 rounded-full bg-primary-700/40 blur-md animate-pulse" style={{ animationDelay: '0.5s' }} />
                <div className="absolute top-1/2 -right-10 w-8 h-8 rounded-full bg-accent-400/30 blur-sm animate-pulse" style={{ animationDelay: '1s' }} />
                
                {/* Corner accent */}
                <div className="absolute -top-1 -left-1 w-8 h-8 border-t-2 border-l-2 border-accent-400/50 rounded-tl-2xl" />
                <div className="absolute -bottom-1 -right-1 w-8 h-8 border-b-2 border-r-2 border-accent-400/50 rounded-br-2xl" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ================= FEATURES GRID ================= */}
      <section className="py-20 sm:py-28 bg-white dark:bg-[#0d1612]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section header */}
          <div className="flex items-center gap-4 mb-12">
            <hr className="flex-1 editorial-rule" />
            <div className="rule-label">
              <span>Capabilities</span>
            </div>
            <hr className="flex-1 editorial-rule" />
          </div>

          <h2 className="font-serif text-2xl sm:text-3xl font-semibold text-stone-900 dark:text-stone-50 mb-4 text-center">
            Everything you need for Ayurvedic innovation
          </h2>
          <p className="text-stone-600 dark:text-stone-400 text-center mb-12 max-w-2xl mx-auto">
            From patent scrutiny to regulatory classification — a single, trustworthy companion for
            Traditional Knowledge compliance.
          </p>

          {/* Features grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((feature, idx) => (
              <div
                key={idx}
                className="answer-card p-6 rounded-lg reveal is-visible"
                style={{ animationDelay: `${idx * 0.1}s` }}
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="font-serif text-lg font-semibold text-stone-900 dark:text-stone-100">
                    {feature.title}
                  </h3>
                  <span className="micro-mono text-xs text-primary-600 dark:text-accent-400 tabular">
                    {feature.stat}
                  </span>
                </div>
                <p className="text-sm text-stone-600 dark:text-stone-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================= HOW IT WORKS ================= */}
      <section className="py-20 sm:py-28 bg-stone-100 dark:bg-[#0a1310]">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section header */}
          <div className="text-center mb-16">
            <div className="rule-label justify-center mb-6">
              <span>The Process</span>
            </div>
            <h2 className="font-serif text-2xl sm:text-3xl font-semibold text-stone-900 dark:text-stone-50 mb-4">
              Three steps to verified guidance
            </h2>
          </div>

          {/* Steps */}
          <div className="space-y-8">
            {[
              {
                step: '01',
                title: 'Ask Your Question',
                description: 'Describe your formulation or legal query in plain language — any supported tongue.',
              },
              {
                step: '02',
                title: 'Grounded Analysis',
                description: 'We retrieve the relevant statutes and generate a response bound to their exact provisions.',
              },
              {
                step: '03',
                title: 'Verified Answers',
                description: 'Receive guidance with authoritative citations and a transparent confidence rating.',
              },
            ].map((item, idx) => (
              <div
                key={idx}
                className="flex gap-6 items-start reveal is-visible"
                style={{ animationDelay: `${idx * 0.15}s` }}
              >
                <div className="micro-mono text-2xl font-semibold text-primary-700 dark:text-accent-400 tabular shrink-0">
                  {item.step}
                </div>
                <div className="flex-1 pt-1">
                  <h3 className="font-serif text-xl font-semibold text-stone-900 dark:text-stone-100 mb-2">
                    {item.title}
                  </h3>
                  <p className="text-stone-600 dark:text-stone-400 leading-relaxed">
                    {item.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================= CTA SECTION ================= */}
      <section className="py-20 sm:py-28 bg-primary-900 dark:bg-[#0a1310] text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-900 to-primary-800 dark:from-[#0a1310] dark:to-[#0d1a15]" />
        
        <div className="relative max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-xs font-semibold mb-8 border border-white/20">
            <HiCheckCircle className="w-4 h-4 text-accent-300" />
            <span className="tracking-wider uppercase">Free to use · No registration required</span>
          </div>
          
          <h2 className="font-serif text-2xl sm:text-4xl font-semibold mb-6 leading-tight">
            Ready to navigate Ayurvedic IPR with confidence?
          </h2>
          
          <p className="text-stone-300 mb-10 max-w-xl mx-auto leading-relaxed">
            Join practitioners, researchers, and pharmaceutical innovators who rely on AyurPedia
            for grounded, citation-first legal intelligence.
          </p>
          
          <button
            onClick={() => navigate('/chat')}
            className="group inline-flex items-center justify-center gap-2 w-full sm:w-auto px-8 py-4 text-sm font-semibold text-primary-900 bg-accent-500 hover:bg-accent-400 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <HiSparkles className="w-5 h-5" />
            <span>Get Started Now</span>
            <HiArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </button>
        </div>
      </section>
    </div>
  );
};

export default LandingView;
