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

export default {
  sendMessage,
  checkHealth,
};
