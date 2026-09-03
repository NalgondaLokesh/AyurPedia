import React, { createContext, useContext, useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { sendMessage as apiSendMessage } from '../services/chatApi';
import { translateText, detectLanguage } from '../services/translationApi';
import { useApp } from './AppContext';
import { useAuth } from './AuthContext';
import toast from 'react-hot-toast';

const ChatContext = createContext(null);

const INITIAL_WELCOME_MESSAGE = {
  id: 'welcome-msg',
  sender: 'assistant',
  text: 'Hello! I am **AyurPedia**, your specialized AI assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, Traditional Knowledge Digital Library (TKDL) norms, and regulatory frameworks (e.g. FSSAI Ayurveda-Aahar, WIPO GRATK Treaty).\n\nYou can ask a regulatory or legal question directly, or use our **Classification Tool** to categorize your herbal formulation.',
  citations: [],
  confidence: 'High',
  jurisdiction: 'India',
  timestamp: new Date().toISOString(),
  disclaimer: 'This is information, not legal advice. Consult a qualified legal professional.',
};

export const ChatProvider = ({ children }) => {
  const { language, jurisdiction } = useApp();
  const { user } = useAuth();
  
  // One-time cleanup of old localStorage keys on mount
  useEffect(() => {
    // Clear all old keys without jurisdiction suffix
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && (key.startsWith('ayurpedia_chat_messages_') || key.startsWith('ayurpedia_conv_id_'))) {
        // Check if key doesn't have jurisdiction suffix (no _India, _International, _Both)
        if (!key.match(/_(India|International|Both)$/)) {
          keysToRemove.push(key);
        }
      }
    }
    keysToRemove.forEach(key => localStorage.removeItem(key));
    console.log('Cleared old localStorage keys:', keysToRemove);
  }, []); // Run once on mount

  const [messages, setMessages] = useState(() => {
    const userId = user?.id || localStorage.getItem('current_user_id') || 'guest';
    const saved = localStorage.getItem(`ayurpedia_chat_messages_${userId}_${jurisdiction}`);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error('Failed to parse saved chat messages:', e);
      }
    }
    return [INITIAL_WELCOME_MESSAGE];
  });

  const [conversationId, setConversationId] = useState(() => {
    const userId = user?.id || localStorage.getItem('current_user_id') || 'guest';
    return localStorage.getItem(`ayurpedia_conv_id_${userId}_${jurisdiction}`) || uuidv4();
  });

  const [isLoading, setIsLoading] = useState(false);
  const [activeClassification, setActiveClassification] = useState(null);
  const [error, setError] = useState(null);

  // Sync messages to localStorage with user-specific and jurisdiction-specific key
  useEffect(() => {
    const userId = user?.id || localStorage.getItem('current_user_id') || 'guest';
    localStorage.setItem(`ayurpedia_chat_messages_${userId}_${jurisdiction}`, JSON.stringify(messages));
  }, [messages, user, jurisdiction]);

  useEffect(() => {
    const userId = user?.id || localStorage.getItem('current_user_id') || 'guest';
    localStorage.setItem(`ayurpedia_conv_id_${userId}_${jurisdiction}`, conversationId);
  }, [conversationId, user, jurisdiction]);

  // Clear chat when user changes or logs out
  useEffect(() => {
    if (!user) {
      // User logged out, clear chat
      setMessages([INITIAL_WELCOME_MESSAGE]);
      setConversationId(uuidv4());
      setActiveClassification(null);
    }
  }, [user]);

  // Load jurisdiction-specific chat when jurisdiction changes
  useEffect(() => {
    const userId = user?.id || localStorage.getItem('current_user_id') || 'guest';
    const saved = localStorage.getItem(`ayurpedia_chat_messages_${userId}_${jurisdiction}`);
    if (saved) {
      try {
        setMessages(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to parse saved chat messages:', e);
        setMessages([INITIAL_WELCOME_MESSAGE]);
      }
    } else {
      setMessages([INITIAL_WELCOME_MESSAGE]);
    }
    // Generate new conversation ID for this jurisdiction
    setConversationId(uuidv4());
    setActiveClassification(null);
  }, [jurisdiction, user]);

  /**
   * Send a chat message through translation and RAG pipeline
   */
  const sendMessage = async (userText) => {
    if (!userText || !userText.trim() || isLoading) return;

    const trimmedText = userText.trim();
    const userMsgId = uuidv4();
    const assistantMsgId = uuidv4();

    // 1. Append User Message
    const userMessage = {
      id: userMsgId,
      sender: 'user',
      text: trimmedText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // 2. Call backend API with selected language (Gemini 2.5 Flash handles multilingual RAG natively)
      const activeLang = language || 'en';
      const responseData = await apiSendMessage({
        query: trimmedText,
        jurisdiction: jurisdiction,
        language: activeLang,
        conversationId: conversationId,
        classification: activeClassification ? {
          category: activeClassification.category,
          relevant_laws: activeClassification.relevant_laws || []
        } : undefined,
      });

      const responseText = responseData.response || 'No response generated.';

      // 5. Append Assistant Message
      const assistantMessage = {
        id: assistantMsgId,
        sender: 'assistant',
        text: responseText,
        citations: responseData.citations || [],
        confidence: responseData.confidence || 'Medium',
        jurisdiction: responseData.jurisdiction || jurisdiction,
        disclaimer: responseData.disclaimer || 'This is information, not legal advice. Consult a qualified legal professional.',
        classification: responseData.classification,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      const userErr = err.userMessage || 'Failed to process your request. Please ensure the backend is running.';
      setError(userErr);
      toast.error(userErr);

      const errorMessage = {
        id: assistantMsgId,
        sender: 'assistant',
        text: `⚠️ **Error**: ${userErr}\n\nPlease try again or contact a legal facilitator if the problem persists.`,
        citations: [],
        confidence: 'Low',
        jurisdiction: jurisdiction,
        timestamp: new Date().toISOString(),
        isError: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearMessages = () => {
    setMessages([INITIAL_WELCOME_MESSAGE]);
    setConversationId(uuidv4());
    setActiveClassification(null);
    toast.success('Chat cleared');
  };

  const attachClassification = (classificationResult) => {
    setActiveClassification(classificationResult);
    toast.success(`Classification attached: ${classificationResult.category}`);
  };

  const removeClassification = () => {
    setActiveClassification(null);
    toast('Classification context removed');
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        isLoading,
        error,
        conversationId,
        activeClassification,
        sendMessage,
        clearMessages,
        attachClassification,
        removeClassification,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
};

export default ChatContext;
