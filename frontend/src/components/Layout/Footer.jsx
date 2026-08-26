import React from 'react';
import { Link } from 'react-router-dom';
import { HiShieldCheck } from 'react-icons/hi2';
import { AyurMark, Diamond } from '../Common/Botanical';

export const Footer = () => {
  return (
    <footer className="mt-auto bg-primary-900 dark:bg-[#0a1310] text-stone-300 text-xs relative overflow-hidden">
      <div className="h-0.5 w-full bg-gradient-to-r from-transparent via-accent-400/60 to-transparent" />
      <div className="pattern-leaf absolute inset-0 opacity-40 pointer-events-none" />
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-5">

          {/* Left brand */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-primary-800 ring-1 ring-accent-400/25 flex items-center justify-center text-accent-300">
              <AyurMark className="w-5 h-5" />
            </div>
            <div className="leading-tight">
              <span className="font-serif text-base font-semibold text-stone-100">
                Ayur<span className="text-accent-400">Pedia</span>
              </span>
              <p className="text-[11px] text-stone-400">Multilingual Ayurvedic IPR Intelligence</p>
            </div>
          </div>

          {/* Center disclaimer reminder */}
          <div className="flex items-center gap-2 text-stone-400 text-[11px] text-center">
            <HiShieldCheck className="w-4 h-4 text-accent-400 shrink-0" />
            <span>AI Regulatory Assistance &middot; Every answer grounded in verified citations</span>
          </div>

          {/* Right links */}
          <div className="flex items-center gap-5 text-stone-300 font-medium">
            <Link to="/disclaimer" className="hover:text-accent-300 transition-colors">Disclaimer</Link>
            <Link to="/privacy" className="hover:text-accent-300 transition-colors">Privacy</Link>
            <Link to="/terms" className="hover:text-accent-300 transition-colors">Terms</Link>
          </div>
        </div>

        <div className="mt-6 flex items-center justify-center gap-3 text-accent-400/50">
          <span className="h-px w-16 bg-gradient-to-r from-transparent to-accent-400/40" />
          <Diamond className="w-2.5 h-2.5" />
          <span className="h-px w-16 bg-gradient-to-l from-transparent to-accent-400/40" />
        </div>

        <p className="mt-4 text-center text-[11px] text-stone-400/80">
          &copy; {new Date().getFullYear()} AyurPedia &middot; Built for Ayurvedic Practitioners, Researchers &amp; Pharmaceutical Innovators
        </p>
      </div>
    </footer>
  );
};

export default Footer;
