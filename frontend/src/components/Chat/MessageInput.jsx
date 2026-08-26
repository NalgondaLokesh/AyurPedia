import React, { useState, useRef, useEffect } from 'react';
import { useChatContext } from '../../context/ChatContext';
import { useApp } from '../../context/AppContext';
import { HiPaperAirplane, HiMicrophone, HiArrowPath } from 'react-icons/hi2';
import toast from 'react-hot-toast';

export const MessageInput = () => {
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const { sendMessage, isLoading } = useChatContext();
  const { language } = useApp();
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [inputText]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    sendMessage(inputText);
    setInputText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Voice Input (Web Speech API with language support)
  const handleVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      toast.error('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      
      // Map language code to BCP 47 tag
      const langMap = {
        en: 'en-IN',
        hi: 'hi-IN',
        bn: 'bn-IN',
        ta: 'ta-IN',
        te: 'te-IN',
        mr: 'mr-IN',
        kn: 'kn-IN',
        ml: 'ml-IN',
        gu: 'gu-IN',
        pa: 'pa-IN',
      };
      recognition.lang = langMap[language] || 'en-IN';

      recognition.onstart = () => {
        setIsListening(true);
        toast('🎙️ Listening... Speak your legal or formulation question.');
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputText((prev) => (prev ? `${prev} ${transcript}` : transcript));
        setIsListening(false);
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        toast.error(`Voice input error: ${event.error}`);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
    } catch (err) {
      console.error('Voice setup error:', err);
      setIsListening(false);
    }
  };

  return (
    <div className="relative">
      <form
        onSubmit={handleSubmit}
        className="relative bg-white dark:bg-primary-950/50 rounded-2xl border border-stone-300/80 dark:border-primary-900/50 shadow-subtle focus-within:border-primary-600 focus-within:ring-2 focus-within:ring-accent-400/25 transition-all duration-300 p-2 hover:shadow-card"
      >
        <div className="flex items-end gap-2">
          {/* Text input */}
          <textarea
            ref={textareaRef}
            rows="1"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder={
              language === 'hi'
                ? 'आयुर्वेदिक कानून या योग के बारे में पूछें... (Enter दबाएं)'
                : 'Ask an Ayurvedic IPR, TKDL or regulatory question... (Press Enter to send)'
            }
            className="w-full max-h-36 py-2 px-2.5 text-xs sm:text-sm text-stone-800 dark:text-stone-100 placeholder-stone-400 dark:placeholder-stone-500 bg-transparent border-none outline-none resize-none leading-relaxed transition-all duration-200"
          />

          {/* Action buttons */}
          <div className="flex items-center gap-1.5 pb-1 shrink-0">
            {/* Voice Input */}
            <button
              type="button"
              onClick={handleVoiceInput}
              disabled={isLoading}
              title={isListening ? 'Listening...' : 'Voice input (Speech to Text)'}
              className={`p-2 rounded-xl transition-all duration-200 cursor-pointer focus-premium ${
                isListening
                  ? 'bg-clay-500 text-white animate-pulse shadow-lg shadow-clay-500/30'
                  : 'text-stone-500 hover:text-primary-800 dark:text-stone-400 dark:hover:text-accent-300 hover:bg-stone-100 dark:hover:bg-primary-900/40 hover:shadow-sm'
              }`}
            >
              <HiMicrophone className="w-5 h-5" />
            </button>

            {/* Send Button */}
            <button
              type="submit"
              disabled={isLoading || !inputText.trim()}
              title="Send message"
              className={`p-2.5 rounded-xl transition-all duration-200 font-semibold flex items-center justify-center ${
                !inputText.trim() || isLoading
                  ? 'bg-stone-200 text-stone-400 cursor-not-allowed dark:bg-primary-900/50 dark:text-stone-500'
                  : 'btn-premium text-white active:scale-95 cursor-pointer'
              }`}
            >
              {isLoading ? (
                <HiArrowPath className="w-5 h-5 animate-spin-slow" />
              ) : (
                <HiPaperAirplane className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </form>
      <div className="flex items-center justify-between px-2 pt-1.5 text-[10px] text-stone-400 dark:text-stone-500">
        <span className="hidden sm:inline">Shift + Enter for new line</span>
        <span className="flex items-center gap-1 mx-auto sm:mx-0">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          <span className="sm:hidden">Verified legal sources</span>
          <span className="hidden sm:inline">Backed by verified statutory legal sources</span>
        </span>
      </div>
    </div>
  );
};

export default MessageInput;
