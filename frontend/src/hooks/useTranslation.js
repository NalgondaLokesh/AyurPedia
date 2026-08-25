import { useState, useCallback } from 'react';
import { translateText, detectLanguage, SUPPORTED_LANGUAGES } from '../services/translationApi';
import { useApp } from '../context/AppContext';

export const useTranslation = () => {
  const { language, setLanguage } = useApp();
  const [isTranslating, setIsTranslating] = useState(false);

  const translate = useCallback(
    async (text, targetLang = language, sourceLang = 'en') => {
      if (!text || targetLang === sourceLang) return text;
      setIsTranslating(true);
      try {
        const translated = await translateText(text, sourceLang, targetLang);
        return translated;
      } catch (e) {
        console.error('Translation error:', e);
        return text;
      } finally {
        setIsTranslating(false);
      }
    },
    [language]
  );

  const translateToEnglish = useCallback(
    async (text) => {
      const detected = detectLanguage(text);
      if (detected === 'en') return text;
      return translate(text, 'en', detected);
    },
    [translate]
  );

  const translateFromEnglish = useCallback(
    async (text, targetLang = language) => {
      if (targetLang === 'en') return text;
      return translate(text, targetLang, 'en');
    },
    [language, translate]
  );

  return {
    language,
    setLanguage,
    supportedLanguages: SUPPORTED_LANGUAGES,
    isTranslating,
    translate,
    translateToEnglish,
    translateFromEnglish,
  };
};

export default useTranslation;
