import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  HiShieldCheck, HiDocumentMagnifyingGlass, HiChatBubbleLeftRight, HiArrowRight,
  HiGlobeAmericas, HiScale, HiBeaker, HiCheckCircle, HiLanguage, HiBookOpen
} from 'react-icons/hi2';
import { Sprig, Mandala, Diamond, Leaf } from '../components/Common/Botanical';

export const LandingView = () => {
  const navigate = useNavigate();

  const FEATURES = [
    {
      icon: HiDocumentMagnifyingGlass,
      title: 'Formulation Classification',
      description: 'Categorise herbal products across 7 statutory classes with grounded AI analysis.',
    },
    {
      icon: HiChatBubbleLeftRight,
      title: 'Legal Intelligence Chat',
      description: 'Interactive Q&A with verified statutory citations and calibrated confidence scoring.',
    },
    {
      icon: HiShieldCheck,
      title: 'Citation Enforcement',
      description: 'Every answer is backed by authoritative legal documents — never unsupported claims.',
    },
    {
      icon: HiLanguage,
      title: 'Multilingual Support',
      description: '10+ Indian languages with real-time translation, so guidance meets you in your tongue.',
    },
    {
      icon: HiScale,
      title: 'Jurisdiction Toggle',
      description: 'Move seamlessly between Indian and International legal frameworks in a single click.',
    },
    {
      icon: HiBeaker,
      title: 'Ayurveda-Focused',
      description: 'Purpose-built for Ayurvedic IPR, TKDL prior art, and Traditional Knowledge compliance.',
    },
  ];

  const STATS = [
    { value: '7', suffix: '+', label: 'Regulatory Classes' },
    { value: '10', suffix: '+', label: 'Indian Languages' },
    { value: '95', suffix: '%', label: 'Citation Accuracy' },
    { value: '2.5', suffix: 's', label: 'Avg Response Time' },
  ];

  const FRAMEWORKS = [
    'Patents Act 1970', 'Biological Diversity Act 2002', 'FSSAI Ayurveda-Aahar',
    'WIPO GRATK 2024', 'TRIPS', 'Nagoya Protocol',
  ];

  const STEPS = [
    { step: 'I', title: 'Ask Your Question', description: 'Describe your formulation or legal query in plain language — any supported tongue.' },
    { step: 'II', title: 'Grounded Analysis', description: 'We retrieve the relevant statutes and generate a response bound to their exact provisions.' },
    { step: 'III', title: 'Verified Answers', description: 'Receive guidance with authoritative citations and a transparent confidence rating.' },
  ];

  return (
    <div className="relative">
      {/* ================= HERO ================= */}
      <section className="relative overflow-hidden">
        {/* Botanical / mandala ornaments */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
          <Mandala className="absolute -top-24 -right-24 w-[26rem] h-[26rem] text-primary-700/10 dark:text-primary-300/10 animate-pulse-slow" />
          <Sprig className="absolute top-24 -left-10 w-40 h-40 text-primary-700/10 dark:text-accent-400/10 animate-sway" />
          <Leaf className="absolute bottom-10 right-16 w-24 h-24 text-accent-500/10 animate-float" />
        </div>

        <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-14 pb-14 sm:pt-28 sm:pb-24 text-center">
          {/* Headline */}
          <h1 className="font-serif font-semibold tracking-tightest text-stone-900 dark:text-stone-50 mb-6 fade-in">
            <span className="block text-[2.5rem] leading-[1.08] sm:text-6xl lg:text-[4.25rem] sm:leading-[1.05]">
              Ancient wisdom,
            </span>
            <span className="block text-[2.5rem] leading-[1.08] sm:text-6xl lg:text-[4.25rem] sm:leading-[1.05]">
              <span className="gradient-text-heritage italic">modern</span> IP clarity.
            </span>
          </h1>

          <p className="text-base sm:text-lg text-stone-600 dark:text-stone-300 mb-9 sm:mb-10 max-w-2xl mx-auto leading-relaxed fade-in delay-100">
            AyurPedia is your AI companion for navigating the intersection of Ayurvedic formulations
            and intellectual property law — grounded, cited, and multilingual.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-3 mb-12 sm:mb-14 fade-in delay-200">
            <button
              onClick={() => navigate('/chat')}
              className="group inline-flex items-center justify-center gap-2 w-full sm:w-auto px-7 py-3.5 text-sm font-semibold text-white btn-premium rounded-2xl cursor-pointer"
            >
              <HiChatBubbleLeftRight className="w-5 h-5 text-accent-300" />
              <span>Start Legal Chat</span>
              <HiArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </button>
            <button
              onClick={() => navigate('/classify')}
              className="inline-flex items-center justify-center gap-2 w-full sm:w-auto px-7 py-3.5 text-sm font-semibold text-primary-800 dark:text-stone-100 bg-white dark:bg-primary-900/40 hover:bg-stone-50 dark:hover:bg-primary-900/60 border border-stone-300/80 dark:border-primary-800/60 rounded-2xl shadow-subtle hover:shadow-card transition-all duration-300 active:scale-95 cursor-pointer"
            >
              <HiDocumentMagnifyingGlass className="w-5 h-5 text-accent-600 dark:text-accent-400" />
              <span>Classify a Formulation</span>
            </button>
          </div>

          {/* Stats strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 max-w-3xl mx-auto rounded-3xl border border-stone-200/80 dark:border-primary-900/40 bg-white/60 dark:bg-primary-950/30 backdrop-blur-sm divide-x divide-y sm:divide-y-0 divide-stone-200/70 dark:divide-primary-900/40 overflow-hidden fade-in delay-300">
            {STATS.map((stat, idx) => (
              <div key={idx} className="p-4 sm:p-5">
                <div className="font-serif text-3xl sm:text-4xl font-semibold text-primary-800 dark:text-stone-100">
                  {stat.value}<span className="text-accent-500">{stat.suffix}</span>
                </div>
                <div className="text-[11px] text-stone-500 dark:text-stone-400 font-medium mt-1 tracking-wide uppercase">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Frameworks marquee-style strip */}
        <div className="relative border-y border-stone-200/70 dark:border-primary-900/40 bg-stone-100/50 dark:bg-primary-950/30">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-stone-500 dark:text-stone-400">
              <span className="overline text-primary-700 dark:text-accent-300 flex items-center gap-1.5">
                <HiBookOpen className="w-4 h-4" /> Grounded in
              </span>
              {FRAMEWORKS.map((f, i) => (
                <span key={i} className="text-xs font-semibold tracking-wide">{f}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ================= FEATURES ================= */}
      <section className="py-16 sm:py-28">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 sm:mb-14 max-w-2xl mx-auto">
            <div className="heritage-divider mb-5">
              <span className="overline text-primary-700 dark:text-accent-300">Capabilities</span>
            </div>
            <h2 className="font-serif text-[1.75rem] sm:text-4xl font-semibold text-stone-900 dark:text-stone-50 mb-4 tracking-tight">
              Everything you need for Ayurvedic innovation
            </h2>
            <p className="text-stone-600 dark:text-stone-400 leading-relaxed">
              From patent scrutiny to regulatory classification — a single, trustworthy companion for
              Traditional Knowledge compliance.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
            {FEATURES.map((feature, idx) => (
              <div
                key={idx}
                className="group premium-card card-accent-top p-6 sm:p-7 rounded-2xl cursor-default slide-in-bottom"
                style={{ animationDelay: `${0.06 * idx}s` }}
              >
                <div className="w-12 h-12 rounded-xl bg-primary-800 text-accent-300 flex items-center justify-center ring-1 ring-primary-700/40 mb-5 transition-all duration-300 group-hover:bg-primary-700 group-hover:-translate-y-0.5">
                  <feature.icon className="w-6 h-6" />
                </div>
                <h3 className="font-serif text-lg font-semibold text-stone-900 dark:text-stone-100 mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-stone-600 dark:text-stone-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================= HOW IT WORKS ================= */}
      <section className="py-16 sm:py-28 bg-stone-100/60 dark:bg-primary-950/20 border-y border-stone-200/70 dark:border-primary-900/40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 sm:mb-16 max-w-2xl mx-auto">
            <div className="heritage-divider mb-5">
              <span className="overline text-primary-700 dark:text-accent-300">The Process</span>
            </div>
            <h2 className="font-serif text-[1.75rem] sm:text-4xl font-semibold text-stone-900 dark:text-stone-50 tracking-tight">
              Three steps to verified guidance
            </h2>
          </div>

          <div className="relative grid grid-cols-1 md:grid-cols-3 gap-10">
            {/* connecting line */}
            <div className="hidden md:block absolute top-10 left-[16%] right-[16%] h-px bg-gradient-to-r from-transparent via-accent-400/40 to-transparent" />
            {STEPS.map((item, idx) => (
              <div key={idx} className="relative flex flex-col items-center text-center">
                <div className="relative w-20 h-20 rounded-full bg-stone-50 dark:bg-primary-900/60 border border-accent-400/40 flex items-center justify-center text-primary-800 dark:text-accent-300 shadow-subtle mb-6">
                  <span className="font-serif text-2xl font-semibold">{item.step}</span>
                  <span className="absolute -bottom-1.5 bg-accent-500 text-white text-[10px] font-bold w-6 h-6 rounded-full flex items-center justify-center shadow-card">{idx + 1}</span>
                </div>
                <h3 className="font-serif text-xl font-semibold text-stone-900 dark:text-stone-100 mb-2">
                  {item.title}
                </h3>
                <p className="text-sm text-stone-600 dark:text-stone-400 leading-relaxed max-w-xs">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================= CTA BAND ================= */}
      <section className="py-16 sm:py-28 bg-primary-900 dark:bg-[#0a1310] text-white relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0" aria-hidden="true">
          <Mandala className="absolute -bottom-28 -left-24 w-[28rem] h-[28rem] text-accent-400/10" />
          <Sprig className="absolute top-6 right-10 w-32 h-32 text-accent-400/10 animate-sway" />
          <div className="pattern-leaf absolute inset-0 opacity-30" />
        </div>
        <div className="relative max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/10 backdrop-blur-md rounded-full text-[11px] font-semibold mb-8 border border-accent-400/25 text-accent-100">
            <HiCheckCircle className="w-4 h-4 text-accent-300 shrink-0" />
            <span className="tracking-[0.12em] uppercase">Free to use &middot; No registration required</span>
          </div>
          <h2 className="font-serif text-[1.75rem] sm:text-5xl font-semibold mb-5 tracking-tight leading-tight">
            Ready to navigate<br className="hidden sm:block" /> Ayurvedic IPR with confidence?
          </h2>
          <p className="text-stone-300 mb-9 sm:mb-10 max-w-xl mx-auto leading-relaxed">
            Join the practitioners, researchers, and pharmaceutical innovators who rely on AyurPedia
            for grounded, citation-first legal intelligence.
          </p>
          <button
            onClick={() => navigate('/chat')}
            className="group inline-flex items-center justify-center gap-2 w-full sm:w-auto px-8 py-4 text-sm font-semibold text-primary-900 btn-saffron rounded-2xl cursor-pointer"
          >
            <HiChatBubbleLeftRight className="w-5 h-5" />
            <span>Get Started Now</span>
            <HiArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </button>
        </div>
      </section>
    </div>
  );
};

export default LandingView;
