import axios from 'axios';

export const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English', script: 'Latin' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', script: 'Devanagari' },
  { code: 'sa', name: 'Sanskrit', nativeName: 'संस्कृतम्', script: 'Devanagari' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी', script: 'Devanagari' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', script: 'Bengali' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', script: 'Tamil' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', script: 'Telugu' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', script: 'Kannada' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', script: 'Malayalam' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', script: 'Gujarati' },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', script: 'Gurmukhi' },
  { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ', script: 'Odia' },
];

const BHASHINI_API_URL = import.meta.env.VITE_BHASHINI_API_URL || 'https://api.bhashini.gov.in';
const BHASHINI_API_KEY = import.meta.env.VITE_BHASHINI_API_KEY || '';
const BHASHINI_USER_ID = import.meta.env.VITE_BHASHINI_USER_ID || '';
const BHASHINI_PIPELINE_ID = import.meta.env.VITE_BHASHINI_PIPELINE_ID || '';

// In-memory translation cache (key: `${sourceLang}:${targetLang}:${text}`)
const translationCache = new Map();

// Built-in offline dictionary translations for common UI phrases and quick responses
const OFFLINE_DICTIONARY = {
  'hi': {
    'Hello! I can help with Ayurveda IPR and regulatory questions. Start by classifying your formulation, or ask a question directly.': 'नमस्ते! मैं आयुर्वेद आईपीआर और नियामक प्रश्नों में आपकी सहायता कर सकता हूँ। अपने योग को वर्गीकृत करके शुरू करें, या सीधे कोई प्रश्न पूछें।',
    'What is Section 3(p)?': 'पेटेंट अधिनियम की धारा 3(p) क्या है?',
    'What are the disclosure requirements under WIPO GRATK?': 'WIPO GRATK के तहत प्रकटीकरण आवश्यकताएं क्या हैं?',
    'How to register Ayurveda Aahar?': 'आयुर्वेद आहार को कैसे पंजीकृत करें?',
    'Classify Formulation': 'योग का वर्गीकरण करें',
    'Verified': 'सत्यापित',
    'High confidence': 'उच्च विश्वसनीयता',
    'Medium confidence': 'मध्यम विश्वसनीयता',
    'Low confidence': 'निम्न विश्वसनीयता',
    'This is information, not legal advice. Consult a qualified legal professional.': 'यह जानकारी है, कानूनी सलाह नहीं। योग्य कानूनी पेशेवर से परामर्श लें।',
    'Contact Legal Facilitator': 'कानूनी विशेषज्ञ से संपर्क करें',
    'India': 'भारत',
    'International': 'अंतर्राष्ट्रीय',
    'Both': 'दोनों',
  }
};

/**
 * Translate text using Bhashini NMT API or smart offline translation.
 * 
 * @param {string} text - Text to translate
 * @param {string} sourceLang - Source language code (e.g. 'en', 'hi')
 * @param {string} targetLang - Target language code (e.g. 'hi', 'en')
 * @returns {Promise<string>} Translated text
 */
export const translateText = async (text, sourceLang = 'en', targetLang = 'hi') => {
  if (!text || sourceLang === targetLang) {
    return text;
  }

  const cacheKey = `${sourceLang}:${targetLang}:${text}`;
  if (translationCache.has(cacheKey)) {
    return translationCache.get(cacheKey);
  }

  // Check offline dictionary
  if (OFFLINE_DICTIONARY[targetLang] && OFFLINE_DICTIONARY[targetLang][text]) {
    const translation = OFFLINE_DICTIONARY[targetLang][text];
    translationCache.set(cacheKey, translation);
    return translation;
  }

  // If Bhashini API key is configured, call Bhashini
  if (BHASHINI_API_KEY && BHASHINI_API_KEY !== 'your_bhashini_api_key_here') {
    try {
      const response = await axios.post(
        `${BHASHINI_API_URL}/services/inference/pipeline`,
        {
          pipelineTasks: [
            {
              taskType: 'translation',
              config: {
                language: {
                  sourceLanguage: sourceLang,
                  targetLanguage: targetLang,
                },
                serviceId: BHASHINI_PIPELINE_ID || undefined,
              },
            },
          ],
          inputData: {
            input: [{ source: text }],
          },
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': BHASHINI_API_KEY,
            'userID': BHASHINI_USER_ID,
          },
          timeout: 10000,
        }
      );

      const translated = response.data?.pipelineResponse?.[0]?.output?.[0]?.target;
      if (translated) {
        translationCache.set(cacheKey, translated);
        return translated;
      }
    } catch (apiError) {
      console.warn('[Bhashini API] Translation failed, falling back to original/local text:', apiError.message);
    }
  }

  // Fallback: return original text (English/untranslated)
  translationCache.set(cacheKey, text);
  return text;
};

/**
 * Detect script / language of input text (heuristic)
 */
export const detectLanguage = (text) => {
  if (!text) return 'en';
  // Devanagari range: \u0900-\u097F
  if (/[\u0900-\u097F]/.test(text)) return 'hi';
  // Bengali: \u0980-\u09FF
  if (/[\u0980-\u09FF]/.test(text)) return 'bn';
  // Tamil: \u0B80-\u0BFF
  if (/[\u0B80-\u0BFF]/.test(text)) return 'ta';
  // Telugu: \u0C00-\u0C7F
  if (/[\u0C00-\u0C7F]/.test(text)) return 'te';
  // Kannada: \u0C80-\u0CFF
  if (/[\u0C80-\u0CFF]/.test(text)) return 'kn';
  // Malayalam: \u0D00-\u0D7F
  if (/[\u0D00-\u0D7F]/.test(text)) return 'ml';
  // Gujarati: \u0A80-\u0AFF
  if (/[\u0A80-\u0AFF]/.test(text)) return 'gu';
  // Gurmukhi (Punjabi): \u0A00-\u0A7F
  if (/[\u0A00-\u0A7F]/.test(text)) return 'pa';
  // Odia: \u0B00-\u0B7F
  if (/[\u0B00-\u0B7F]/.test(text)) return 'or';

  return 'en';
};

export default {
  SUPPORTED_LANGUAGES,
  translateText,
  detectLanguage,
};
