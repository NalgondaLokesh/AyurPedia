import React, { useState, useRef, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { HiGlobeAlt, HiChevronDown } from 'react-icons/hi2';

export const LanguageSelector = () => {
  const { language, setLanguage, supportedLanguages } = useApp();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const currentLang = supportedLanguages.find((l) => l.code === language) || supportedLanguages[0];

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-stone-700 dark:text-stone-200 bg-white dark:bg-primary-950/50 hover:bg-stone-50 dark:hover:bg-primary-900/50 border border-stone-200 dark:border-primary-900/50 rounded-xl shadow-subtle transition-all focus:outline-none focus:ring-2 focus:ring-accent-400/25"
      >
        <HiGlobeAlt className="w-4 h-4 text-primary-600 dark:text-accent-400" />
        <span>{currentLang.nativeName}</span>
        <span className="text-[10px] text-stone-400 font-normal">({currentLang.code.toUpperCase()})</span>
        <HiChevronDown className={`w-3.5 h-3.5 text-stone-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-1.5 w-48 max-h-64 overflow-y-auto rounded-xl bg-white dark:bg-[#101a15] border border-stone-100 dark:border-primary-900/60 shadow-card py-1 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
          <div className="px-3 py-1.5 text-[10px] uppercase tracking-[0.12em] font-bold text-stone-400 border-b border-stone-100 dark:border-primary-900/50">
            Select Language
          </div>
          {supportedLanguages.map((lang) => {
            const isSelected = lang.code === language;
            return (
              <button
                key={lang.code}
                onClick={() => {
                  setLanguage(lang.code);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between transition-colors ${
                  isSelected
                    ? 'bg-accent-50 dark:bg-accent-500/15 text-primary-700 dark:text-accent-200 font-bold'
                    : 'text-stone-700 dark:text-stone-300 hover:bg-stone-50 dark:hover:bg-primary-900/40'
                }`}
              >
                <div>
                  <span className="block font-medium">{lang.nativeName}</span>
                  <span className="text-[10px] text-stone-400">{lang.name}</span>
                </div>
                {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-accent-500"></span>}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default LanguageSelector;
