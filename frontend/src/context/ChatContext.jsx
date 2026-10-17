import React, { createContext, useContext, useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { sendMessage as apiSendMessage, getConversation, listConversations, createConversation } from '../services/chatApi';
import { translateText, detectLanguage } from '../services/translationApi';
import { useApp } from './AppContext';
import { useAuth } from './AuthContext';
import api from '../services/api';
import toast from 'react-hot-toast';

const ChatContext = createContext(null);

const getWelcomeMessage = async (language) => {
  const baseText = 'Hello! I am **AyurPedia**, your specialized AI assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, Traditional Knowledge Digital Library (TKDL) norms, and regulatory frameworks (e.g. FSSAI Ayurveda-Aahar, WIPO GRATK Treaty).\n\nYou can ask a regulatory or legal question directly, or use our **Classification Tool** to categorize your herbal formulation.';
  
  try {
    const translatedText = await translateText(baseText, 'en', language);
    return {
      id: 'welcome-msg',
      sender: 'assistant',
      text: translatedText,
      citations: [],
      confidence: 'High',
      jurisdiction: 'India',
      timestamp: new Date().toISOString(),
      disclaimer: 'This is information, not legal advice. Consult a qualified legal professional.',
    };
  } catch (error) {
    console.error('Failed to translate welcome message:', error);
    return {
      id: 'welcome-msg',
      sender: 'assistant',
      text: baseText,
      citations: [],
      confidence: 'High',
      jurisdiction: 'India',
      timestamp: new Date().toISOString(),
      disclaimer: 'This is information, not legal advice. Consult a qualified legal professional.',
    };
  }
};

export const ChatProvider = ({ children }) => {
  const { language, jurisdiction } = useApp();
  const { user } = useAuth();

  const [messages, setMessages] = useState([]);
  const [welcomeMessage, setWelcomeMessage] = useState(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [activeClassification, setActiveClassification] = useState(null);

  // Load welcome message based on language
  useEffect(() => {
    const loadWelcomeMessage = async () => {
      const msg = await getWelcomeMessage(language);
      setWelcomeMessage(msg);
    };
    loadWelcomeMessage();
  }, [language]);

  // Load conversation history from MongoDB when user or jurisdiction changes
  useEffect(() => {
    const loadConversationHistory = async () => {
      if (!user) {
        // Not logged in, use welcome message
        if (welcomeMessage) {
          setMessages([welcomeMessage]);
        }
        setConversationId(null);
        return;
      }

      setIsLoadingHistory(true);
      try {
        const conversations = await listConversations(20);
        if (conversations && conversations.length > 0) {
          // Load the most recent conversation for the current jurisdiction
          const matchingConv = conversations.find(
            (c) => c.jurisdiction === jurisdiction
          );
          if (matchingConv) {
            setConversationId(matchingConv.conversation_id);
            const convData = await getConversation(matchingConv.conversation_id);
            if (convData && convData.messages) {
              // Ensure each message has an id field (use _id from MongoDB if id is missing)
              const messagesWithIds = convData.messages.map(msg => ({
                ...msg,
                id: msg.id || msg._id || uuidv4()
              }));
              setMessages(messagesWithIds);
            } else {
              // Conversation exists but has no messages
              setMessages([welcomeMessage]);
            }
          } else {
            // No matching conversation, create new one
            const newConv = await createConversation(jurisdiction, language);
            setConversationId(newConv.conversation_id);
            setMessages([welcomeMessage]);
          }
        } else {
          // No conversations, create new one
          const newConv = await createConversation(jurisdiction, language);
          setConversationId(newConv.conversation_id);
          setMessages([welcomeMessage]);
        }
      } catch (error) {
        console.error('Failed to load conversation history:', error);
        // Fallback to welcome message
        if (welcomeMessage) {
          setMessages([welcomeMessage]);
        }
      } finally {
        setIsLoadingHistory(false);
      }
    };

    loadConversationHistory();
  }, [user, jurisdiction, language, welcomeMessage]);

  // Handle user logout
  useEffect(() => {
    if (!user) {
      // User logged out, clear chat
      if (welcomeMessage) {
        setMessages([welcomeMessage]);
      }
      setConversationId(null);
      setActiveClassification(null);
    }
  }, [user, welcomeMessage]);

  /**
   * Send a chat message through translation and RAG pipeline
   */
  const sendMessage = async (userText) => {
    if (!userText || !userText.trim() || isLoading) return;

    const trimmedText = userText.trim();

    // Ensure we have a conversation ID
    let currentConvId = conversationId;
    if (!currentConvId && user) {
      try {
        const newConv = await createConversation(jurisdiction, language);
        currentConvId = newConv.conversation_id;
        setConversationId(currentConvId);
      } catch (error) {
        console.error('Failed to create conversation:', error);
        setError('Failed to create conversation. Please try again.');
        toast.error('Failed to create conversation');
        return;
      }
    }

    // 1. Append User Message with temporary ID
    const userMsgId = uuidv4();
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
        conversationId: currentConvId,
        classification: activeClassification ? {
          category: activeClassification.category,
          relevant_laws: activeClassification.relevant_laws || []
        } : undefined,
      });

      const responseText = responseData.response || 'No response generated.';

      // 3. Append Assistant Message with backend-provided ID if available
      const assistantMessage = {
        id: responseData.assistant_message_id || uuidv4(),
        sender: 'assistant',
        text: responseText,
        citations: responseData.citations || [],
        confidence: responseData.confidence || 'Medium',
        jurisdiction: responseData.jurisdiction || jurisdiction,
        disclaimer: responseData.disclaimer || 'This is information, not legal advice. Consult a qualified legal professional.',
        classification: responseData.classification,
        parent_message_id: responseData.user_message_id || userMsgId,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      const userErr = err.userMessage || 'Failed to process your request. Please ensure the backend is running.';
      setError(userErr);
      toast.error(userErr);

      const errorMessage = {
        id: uuidv4(),
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

  const clearMessages = async () => {
    // Create a new conversation on the backend instead of just generating a local UUID
    try {
      const newConv = await createConversation(jurisdiction, language);
      setConversationId(newConv.conversation_id);
      setMessages([welcomeMessage]);
      setActiveClassification(null);
      toast.success('Chat cleared');
    } catch (error) {
      console.error('Failed to clear chat:', error);
      toast.error('Failed to clear chat');
    }
  };

  const attachClassification = (classificationResult) => {
    setActiveClassification(classificationResult);
    toast.success(`Classification attached: ${classificationResult.category}`);
  };

  const removeClassification = () => {
    setActiveClassification(null);
    toast('Classification context removed');
  };

  const loadConversation = async (convId) => {
    if (!convId) return;
    
    setIsLoadingHistory(true);
    try {
      const convData = await getConversation(convId);
      if (convData && convData.messages) {
        // Use the actual IDs from the database - do not generate new ones
        const messagesWithIds = convData.messages.map(msg => ({
          ...msg,
          id: msg.id || msg._id  // Use existing ID, never generate a new one
        }));
        setMessages(messagesWithIds);
        setConversationId(convId);
      }
    } catch (error) {
      console.error('Failed to load conversation:', error);
      toast.error('Failed to load conversation');
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const deleteMessage = async (messageId) => {
    if (!conversationId || !user) {
      // Not logged in or no conversation, just remove from local state
      setMessages((prev) => {
        const messageToDelete = prev.find((msg) => msg.id === messageId || msg._id === messageId);
        if (!messageToDelete) return prev;
        
        const idsToDelete = [messageId];
        
        // If deleting user message, find assistant message with parent_message_id
        if (messageToDelete.sender === 'user') {
          const assistantMsg = prev.find(msg => msg.parent_message_id === messageId);
          if (assistantMsg) {
            idsToDelete.push(assistantMsg.id || assistantMsg._id);
          }
        }
        // If deleting assistant message, find the user message it references
        else if (messageToDelete.sender === 'assistant' && messageToDelete.parent_message_id) {
          idsToDelete.push(messageToDelete.parent_message_id);
        }
        
        return prev.filter((msg) => !idsToDelete.includes(msg.id) && !idsToDelete.includes(msg._id));
      });
      return;
    }

    try {
      // Find the message to determine pairing
      const messageToDelete = messages.find((msg) => msg.id === messageId || msg._id === messageId);
      if (!messageToDelete) return;
      
      const idsToDelete = [messageId];
      
      // If deleting user message, find assistant message with parent_message_id
      if (messageToDelete.sender === 'user') {
        const assistantMsg = messages.find(msg => msg.parent_message_id === messageId);
        if (assistantMsg) {
          const assistantId = assistantMsg.id || assistantMsg._id;
          if (assistantId) idsToDelete.push(assistantId);
        }
      }
      // If deleting assistant message, find the user message it references
      else if (messageToDelete.sender === 'assistant' && messageToDelete.parent_message_id) {
        idsToDelete.push(messageToDelete.parent_message_id);
      }
      
      // Delete all messages from MongoDB (single API call handles pairing)
      await api.delete(`/api/conversations/${conversationId}/messages/${messageId}`);
      
      // Remove from local state
      setMessages((prev) => prev.filter((msg) => !idsToDelete.includes(msg.id) && !idsToDelete.includes(msg._id)));
      toast.success('Message(s) deleted');
    } catch (error) {
      console.error('Failed to delete message:', error);
      toast.error('Failed to delete message from server');
    }
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
        deleteMessage,
        loadConversation,
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
