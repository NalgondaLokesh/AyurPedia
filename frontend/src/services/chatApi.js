import api from './api';

/**
 * Send a chat query to the backend RAG pipeline.
 * 
 * @param {Object} params
 * @param {string} params.query - User query string
 * @param {string} params.jurisdiction - "India" | "International" | "Both"
 * @param {string} [params.conversationId] - Optional session ID
 * @param {Object} [params.classification] - Optional classification context
 * @returns {Promise<{response: string, citations: Array, confidence: string, disclaimer: string, jurisdiction: string}>}
 */
export const sendMessage = async ({ query, jurisdiction = 'India', language = 'en', conversationId = null, classification = null }) => {
  try {
    const payload = {
      query: query.trim(),
      jurisdiction: jurisdiction || 'India',
      language: language || 'en',
      conversation_id: conversationId,
      classification: classification || undefined,
    };

    const response = await api.post('/api/chat', payload);
    return response.data;
  } catch (error) {
    console.error('Failed in sendMessage:', error);
    throw error;
  }
};

/**
 * Check backend health status
 */
export const checkHealth = async () => {
  try {
    const response = await api.get('/api/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

/**
 * Fetch conversation history from MongoDB
 */
export const getConversation = async (conversationId) => {
  try {
    const response = await api.get(`/api/conversations/${conversationId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch conversation:', error);
    throw error;
  }
};

/**
 * List all conversations for the current user
 */
export const listConversations = async (limit = 20) => {
  try {
    const response = await api.get('/api/conversations', { params: { limit } });
    return response.data;
  } catch (error) {
    console.error('Failed to list conversations:', error);
    throw error;
  }
};

/**
 * Create a new conversation
 */
export const createConversation = async (jurisdiction = 'India', language = 'en') => {
  try {
    const response = await api.post('/api/conversations', {
      jurisdiction,
      language,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to create conversation:', error);
    throw error;
  }
};

export default {
  sendMessage,
  checkHealth,
  getConversation,
  listConversations,
  createConversation,
};
