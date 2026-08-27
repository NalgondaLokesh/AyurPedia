import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { HiChatBubbleLeftRight, HiDocumentMagnifyingGlass, HiBars3, HiXMark, HiUserGroup, HiUser, HiArrowRightOnRectangle, HiSun, HiMoon, HiCog } from 'react-icons/hi2';
import { useApp } from '../../context/AppContext';
import { useAuth } from '../../context/AuthContext';
import JurisdictionToggle from '../Common/JurisdictionToggle';
import LanguageSelector from '../Common/LanguageSelector';
import { AyurMark } from '../Common/Botanical';

export const Header = () => {
  const { openFacilitatorModal, activeTab, setActiveTab, theme, setTheme } = useApp();
  const { user, logout, isAuthenticated } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const isCurrentRoute = (path) => location.pathname === path;
  const isLandingPage = location.pathname === '/' && !isAuthenticated;
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const navLinks = isAuthenticated
    ? [
        { to: '/chat', label: 'Legal Chat', icon: HiChatBubbleLeftRight, tab: 'chat' },
        { to: '/classify', label: 'Classifier', icon: HiDocumentMagnifyingGlass, tab: 'classify' },
      ]
    : [];

  return (
    <header className="sticky top-0 z-40 bg-stone-50/80 dark:bg-[#0d1310]/85 backdrop-blur-xl border-b border-stone-200/70 dark:border-primary-900/40">
      {/* Saffron hairline */}
      <div className="h-0.5 w-full bg-gradient-to-r from-transparent via-accent-400/70 to-transparent" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          
          {/* Logo & Brand */}
          <Link to={isAuthenticated ? '/chat' : '/'} className="flex items-center gap-3 shrink-0 group">
            <div className="relative w-11 h-11 rounded-2xl bg-primary-800 flex items-center justify-center text-accent-300 ring-1 ring-primary-700/50 shadow-card group-hover:ring-accent-400/60 transition-all duration-300 group-hover:-translate-y-0.5">
              <span className="absolute inset-1 rounded-xl border border-accent-400/20" />
              <AyurMark className="w-6 h-6 relative z-10" />
            </div>
            <div className="leading-none">
              <div className="flex items-center gap-1.5">
                <span className="text-xl font-serif font-semibold tracking-tight text-primary-800 dark:text-stone-100">
                  Ayur<span className="text-accent-600 dark:text-accent-400">Pedia</span>
                </span>
              </div>
              <p className="text-[10px] text-stone-500 dark:text-stone-400 font-medium hidden sm:block tracking-[0.14em] uppercase mt-1">
                IPR &amp; Regulatory Intelligence
              </p>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 bg-stone-100/70 dark:bg-primary-950/40 p-1 rounded-full border border-stone-200/80 dark:border-primary-900/40">
            {navLinks.map(({ to, label, icon: Icon, tab }) => {
              const active = tab
                ? (isCurrentRoute(to) && activeTab === tab) || (to === '/classify' && activeTab === 'classify')
                : isCurrentRoute(to);
              return (
                <Link
                  key={to}
                  to={to}
                  onClick={() => tab && setActiveTab(tab)}
                  className={`relative flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold rounded-full transition-all duration-300 ${
                    active
                      ? 'bg-primary-800 text-stone-50 shadow-card'
                      : 'text-stone-600 dark:text-stone-300 hover:text-primary-800 dark:hover:text-stone-100 hover:bg-white/70 dark:hover:bg-primary-900/40'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-accent-300' : 'text-primary-600 dark:text-primary-400'}`} />
                  <span>{label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Right Controls: Jurisdiction + Language + Theme + Auth + Facilitator */}
          <div className="hidden lg:flex items-center gap-2">
            {!isLandingPage && !isAuthPage && <JurisdictionToggle />}
            <LanguageSelector />
            
            <button
              type="button"
              onClick={toggleTheme}
              className="p-2 text-stone-500 hover:text-primary-800 dark:text-stone-400 dark:hover:text-accent-300 rounded-xl hover:bg-stone-100 dark:hover:bg-primary-900/40 transition-all duration-200 cursor-pointer focus-premium"
              title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
            >
              {theme === 'light' ? <HiMoon className="w-5 h-5" /> : <HiSun className="w-5 h-5" />}
            </button>
            
            {isAuthenticated ? (
              <>
                <Link
                  to="/settings"
                  className="p-2 text-stone-500 hover:text-primary-800 dark:text-stone-400 dark:hover:text-accent-300 rounded-xl hover:bg-stone-100 dark:hover:bg-primary-900/40 transition-all duration-200 cursor-pointer focus-premium"
                  title="Settings"
                >
                  <HiCog className="w-5 h-5" />
                </Link>
                <div className="flex items-center gap-2 px-3 py-1.5 bg-stone-100 dark:bg-primary-950/50 rounded-xl border border-stone-200 dark:border-primary-900/50">
                  <HiUser className="w-4 h-4 text-primary-600 dark:text-accent-400" />
                  <span className="text-xs font-medium text-stone-700 dark:text-stone-300">
                    {user?.full_name || user?.email?.split('@')[0]}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={logout}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-stone-700 hover:bg-stone-100 dark:text-stone-300 dark:hover:bg-primary-900/40 rounded-xl transition-all duration-200 cursor-pointer focus-premium"
                  title="Logout"
                >
                  <HiArrowRightOnRectangle className="w-4 h-4" />
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold text-primary-800 dark:text-stone-200 bg-white dark:bg-primary-900/40 hover:bg-stone-100 dark:hover:bg-primary-900/60 border border-stone-200 dark:border-primary-800/60 rounded-xl transition-all duration-200 cursor-pointer focus-premium"
              >
                <HiUser className="w-4 h-4 text-primary-600 dark:text-accent-400" />
                <span>Sign In</span>
              </Link>
            )}
            
            <button
              type="button"
              onClick={() => openFacilitatorModal()}
              className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold text-white btn-premium rounded-xl transition-all duration-200 cursor-pointer"
            >
              <HiUserGroup className="w-4 h-4 text-accent-300" />
              <span>Facilitator</span>
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center gap-1 lg:hidden">
            <button
              type="button"
              onClick={toggleTheme}
              aria-label="Toggle theme"
              className="p-2.5 text-stone-500 hover:text-primary-800 dark:text-stone-400 dark:hover:text-accent-300 rounded-xl hover:bg-stone-100 dark:hover:bg-primary-900/40 transition-colors cursor-pointer"
            >
              {theme === 'light' ? <HiMoon className="w-5 h-5" /> : <HiSun className="w-5 h-5" />}
            </button>
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Open menu"
              aria-expanded={mobileMenuOpen}
              className="p-2.5 text-stone-600 dark:text-stone-300 hover:text-primary-800 hover:bg-stone-100 dark:hover:bg-primary-900/40 rounded-xl focus:outline-none"
            >
              {mobileMenuOpen ? <HiXMark className="w-6 h-6" /> : <HiBars3 className="w-6 h-6" />}
            </button>
          </div>

        </div>

        {/* Mobile Dropdown Panel */}
        {mobileMenuOpen && (
          <div className="lg:hidden py-4 border-t border-stone-200/70 dark:border-primary-900/40 space-y-3 animate-in fade-in slide-in-from-top-2 duration-200">
            {/* Jurisdiction + Language row */}
            {!isLandingPage && !isAuthPage && (
              <div className="flex flex-wrap items-center justify-center gap-2 pb-3">
                <JurisdictionToggle />
                <LanguageSelector />
              </div>
            )}
            {(isLandingPage || isAuthPage) && (
              <div className="flex flex-wrap items-center justify-center gap-2 pb-3">
                <LanguageSelector />
              </div>
            )}
            {navLinks.length > 0 && (
              <div className="grid grid-cols-3 gap-2">
                {navLinks.map(({ to, label, icon: Icon, tab }) => {
                  const active = tab ? activeTab === tab : isCurrentRoute(to);
                  return (
                    <Link
                      key={to}
                      to={to}
                      onClick={() => {
                        if (tab) setActiveTab(tab);
                        setMobileMenuOpen(false);
                      }}
                      className={`flex flex-col items-center justify-center gap-1.5 p-3 text-xs font-semibold rounded-2xl border transition-all duration-200 ${
                      active
                        ? 'bg-primary-800 border-primary-700 text-stone-50 shadow-card'
                        : 'border-stone-200 dark:border-primary-900/50 text-stone-600 dark:text-stone-300 hover:bg-white/70 dark:hover:bg-primary-900/40'
                    }`}
                    >
                      <Icon className={`w-5 h-5 ${active ? 'text-accent-300' : 'text-primary-600 dark:text-primary-400'}`} />
                      <span>{label}</span>
                    </Link>
                  );
                })}
              </div>
            )}
            {isAuthenticated ? (
              <div className="grid grid-cols-2 gap-2">
                <Link
                  to="/settings"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center justify-center gap-2 py-2.5 text-xs font-semibold text-stone-700 dark:text-stone-300 bg-stone-100 dark:bg-primary-950/50 hover:bg-stone-200 dark:hover:bg-primary-900/50 rounded-xl transition-all duration-200 border border-stone-200 dark:border-primary-900/50"
                >
                  <HiCog className="w-4 h-4" />
                  <span>Settings</span>
                </Link>
                <button
                  type="button"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    logout();
                  }}
                  className="flex items-center justify-center gap-2 py-2.5 text-xs font-semibold text-stone-700 dark:text-stone-300 bg-stone-100 dark:bg-primary-950/50 hover:bg-stone-200 dark:hover:bg-primary-900/50 rounded-xl transition-all duration-200 border border-stone-200 dark:border-primary-900/50"
                >
                  <HiArrowRightOnRectangle className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full flex items-center justify-center gap-2 py-2.5 text-xs font-bold text-primary-800 dark:text-stone-200 bg-white dark:bg-primary-900/40 border border-stone-200 dark:border-primary-800/60 rounded-xl transition-all duration-200"
              >
                <HiUser className="w-4 h-4 text-primary-600 dark:text-accent-400" />
                <span>Sign In</span>
              </Link>
            )}
            
            <button
              type="button"
              onClick={() => {
                setMobileMenuOpen(false);
                openFacilitatorModal();
              }}
              className="w-full flex items-center justify-center gap-2 py-2.5 text-xs font-bold text-white btn-premium rounded-xl transition-all duration-200"
            >
              <HiUserGroup className="w-4 h-4 text-accent-300" />
              <span>Contact Legal Facilitator</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
