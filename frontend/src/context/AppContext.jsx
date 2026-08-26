import React, { createContext, useContext, useState, useEffect } from 'react';
import { SUPPORTED_LANGUAGES } from '../services/translationApi';

const AppContext = createContext(null);

export const AppProvider = ({ children }) => {
  // Global State
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('ayurpedia_language') || 'en';
  });

  const [jurisdiction, setJurisdiction] = useState(() => {
    return localStorage.getItem('ayurpedia_jurisdiction') || 'India';
  });

  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('ayurpedia_theme') || 'light';
  });

  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'classify'
  const [isFacilitatorModalOpen, setIsFacilitatorModalOpen] = useState(false);
  const [facilitatorContext, setFacilitatorContext] = useState(null);

  // Sync with localStorage
  useEffect(() => {
    localStorage.setItem('ayurpedia_language', language);
  }, [language]);

  useEffect(() => {
    localStorage.setItem('ayurpedia_jurisdiction', jurisdiction);
  }, [jurisdiction]);

  useEffect(() => {
    localStorage.setItem('ayurpedia_theme', theme);
    // Apply theme to document
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // Initialize theme on mount
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    }
  }, []);

  const openFacilitatorModal = (context = null) => {
    setFacilitatorContext(context);
    setIsFacilitatorModalOpen(true);
  };

  const closeFacilitatorModal = () => {
    setIsFacilitatorModalOpen(false);
    setFacilitatorContext(null);
  };

  return (
    <AppContext.Provider
      value={{
        language,
        setLanguage,
        jurisdiction,
        setJurisdiction,
        theme,
        setTheme,
        activeTab,
        setActiveTab,
        supportedLanguages: SUPPORTED_LANGUAGES,
        isFacilitatorModalOpen,
        openFacilitatorModal,
        closeFacilitatorModal,
        facilitatorContext,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

export default AppContext;
