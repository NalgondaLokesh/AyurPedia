import api from './api';

/**
 * Classify an Ayurvedic formulation via backend API.
 * 
 * @param {string} formulationDescription - Textual description of formulation, ingredients, and intent.
 * @returns {Promise<{category: string, confidence: number, relevant_laws: string[], description: string, jurisdiction: string}>}
 */
export const classifyFormulation = async (formulationDescription) => {
  if (!formulationDescription || formulationDescription.trim().length < 10) {
    throw new Error('Please provide at least 10 characters describing the formulation.');
  }

  try {
    const payload = {
      formulation_description: formulationDescription.trim(),
    };

    const response = await api.post('/api/classify', payload);
    return response.data;
  } catch (error) {
    console.error('Classification request failed:', error);
    throw error;
  }
};

export default {
  classifyFormulation,
};
