import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import JurisdictionToggle from '../Common/JurisdictionToggle';
import LanguageSelector from '../Common/LanguageSelector';
import { HiSparkles, HiUserGroup, HiBars3, HiXMark, HiChatBubbleLeftRight, HiDocumentMagnifyingGlass } from 'react-icons/hi2';

export const Header = () => {
  const { openFacilitatorModal, activeTab, setActiveTab } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const isCurrentRoute = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-40 bg-white/90 dark:bg-stone-900/90 backdrop-blur-md border-b border-stone-200/80 dark:border-stone-800 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-3 shrink-0 group">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-primary-800 via-primary-600 to-herbal-leaf flex items-center justify-center text-white shadow-md shadow-primary-900/15 group-hover:scale-105 transition-transform">
              <span className="text-xl font-bold font-serif">A</span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-lg font-black tracking-tight bg-gradient-to-r from-primary-900 via-primary-700 to-emerald-700 bg-clip-text text-transparent">
                  AyurPedia
                </span>
                <span className="px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-accent-100 text-accent-700 rounded-md">
                  v2.0
                </span>
              </div>
              <p className="text-[10px] text-stone-500 font-medium hidden sm:block">
                Ayurvedic IPR & Regulatory Intelligence
              </p>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 bg-stone-100/80 p-1 rounded-2xl border border-stone-200/60">
            <Link
              to="/"
              onClick={() => setActiveTab('chat')}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-xl transition-all ${
                isCurrentRoute('/') && activeTab === 'chat'
                  ? 'bg-white text-primary-900 shadow-xs'
                  : 'text-stone-600 hover:text-stone-900 hover:bg-stone-200/50'
              }`}
            >
              <HiChatBubbleLeftRight className="w-4 h-4 text-primary-600" />
              <span>Legal Chat</span>
            </Link>

            <Link
              to="/classify"
              onClick={() => setActiveTab('classify')}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-xl transition-all ${
                isCurrentRoute('/classify') || activeTab === 'classify'
                  ? 'bg-white text-primary-900 shadow-xs'
                  : 'text-stone-600 hover:text-stone-900 hover:bg-stone-200/50'
              }`}
            >
              <HiDocumentMagnifyingGlass className="w-4 h-4 text-emerald-600" />
              <span>Formulation Classifier</span>
            </Link>
          </nav>

          {/* Right Controls: Jurisdiction + Language + Facilitator */}
          <div className="hidden lg:flex items-center gap-3">
            <JurisdictionToggle />
            <LanguageSelector />
            <button
              type="button"
              onClick={() => openFacilitatorModal()}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-primary-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-xl transition-colors cursor-pointer"
            >
              <HiUserGroup className="w-4 h-4 text-primary-700" />
              <span>Facilitator</span>
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center gap-2 lg:hidden">
            <LanguageSelector />
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-stone-600 hover:text-stone-900 hover:bg-stone-100 rounded-xl focus:outline-none"
            >
              {mobileMenuOpen ? <HiXMark className="w-6 h-6" /> : <HiBars3 className="w-6 h-6" />}
            </button>
          </div>

        </div>

        {/* Mobile Dropdown Panel */}
        {mobileMenuOpen && (
          <div className="lg:hidden py-3 border-t border-stone-200 space-y-3 animate-in fade-in slide-in-from-top-2 duration-150">
            <div className="flex justify-center pb-2">
              <JurisdictionToggle />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <Link
                to="/"
                onClick={() => {
                  setActiveTab('chat');
                  setMobileMenuOpen(false);
                }}
                className={`flex items-center justify-center gap-1.5 p-2 text-xs font-semibold rounded-xl border ${
                  activeTab === 'chat' ? 'bg-primary-50 border-primary-300 text-primary-900' : 'border-stone-200'
                }`}
              >
                <HiChatBubbleLeftRight className="w-4 h-4 text-primary-600" />
                <span>Chat</span>
              </Link>
              <Link
                to="/classify"
                onClick={() => {
                  setActiveTab('classify');
                  setMobileMenuOpen(false);
                }}
                className={`flex items-center justify-center gap-1.5 p-2 text-xs font-semibold rounded-xl border ${
                  activeTab === 'classify' ? 'bg-primary-50 border-primary-300 text-primary-900' : 'border-stone-200'
                }`}
              >
                <HiDocumentMagnifyingGlass className="w-4 h-4 text-emerald-600" />
                <span>Classifier</span>
              </Link>
            </div>
            <button
              type="button"
              onClick={() => {
                setMobileMenuOpen(false);
                openFacilitatorModal();
              }}
              className="w-full flex items-center justify-center gap-2 py-2 text-xs font-bold text-white bg-primary-700 rounded-xl"
            >
              <HiUserGroup className="w-4 h-4" />
              <span>Contact Legal Facilitator</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
