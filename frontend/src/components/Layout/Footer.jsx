import React from 'react';
import { Link } from 'react-router-dom';
import { HiShieldCheck, HiSparkles } from 'react-icons/hi2';

export const Footer = () => {
  return (
    <footer className="mt-auto bg-stone-100/90 dark:bg-stone-900 border-t border-stone-200/80 dark:border-stone-800 text-stone-600 text-xs py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          
          {/* Left info */}
          <div className="flex items-center gap-2 text-stone-500">
            <span className="font-bold text-stone-800">AyurPedia</span>
            <span>•</span>
            <span>Multilingual Ayurvedic IPR Intelligence</span>
            <span>•</span>
            <span className="font-mono text-[10px] bg-stone-200 px-1.5 py-0.5 rounded">v2.0.0</span>
          </div>

          {/* Center disclaimer reminder */}
          <div className="flex items-center gap-1.5 text-stone-500 text-[11px] text-center">
            <HiShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>AI Regulatory Assistance • Citations ground all answers</span>
          </div>

          {/* Right links */}
          <div className="flex items-center gap-4 text-stone-600 font-medium">
            <Link to="/disclaimer" className="hover:text-primary-700 transition-colors">
              Disclaimer
            </Link>
            <Link to="/privacy" className="hover:text-primary-700 transition-colors">
              Privacy
            </Link>
            <Link to="/terms" className="hover:text-primary-700 transition-colors">
              Terms
            </Link>
          </div>

        </div>
        
        <div className="mt-4 pt-4 border-t border-stone-200/60 text-center text-[10px] text-stone-400">
          © {new Date().getFullYear()} AyurPedia. Built for Ayurvedic Practitioners, Researchers & Pharmaceutical Innovators.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
