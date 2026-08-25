import { useState, useCallback } from 'react';
import { classifyFormulation as apiClassify } from '../services/classifyApi';
import toast from 'react-hot-toast';

export const useClassification = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    isClassical: 'no', // 'yes' | 'no'
    herbs: '',
    intendedUse: 'dietary', // 'dietary' | 'medicinal' | 'cosmetic' | 'wellness'
    description: '',
  });

  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const updateFormData = useCallback((field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  }, []);

  const buildFullDescription = useCallback(() => {
    const { isClassical, herbs, intendedUse, description } = formData;
    let full = '';
    
    if (description && description.trim()) {
      full = description.trim();
    } else {
      const classicalText = isClassical === 'yes' ? 'Classical text formulation' : 'New/proprietary herbal formulation';
      const herbsText = herbs ? `containing herbs: ${herbs}` : '';
      const useText = `intended for ${intendedUse} use`;
      full = `${classicalText} ${herbsText} ${useText}.`;
    }

    return full;
  }, [formData]);

  const classify = async (customDescription = null) => {
    const textToClassify = customDescription || buildFullDescription();
    
    if (!textToClassify || textToClassify.trim().length < 10) {
      toast.error('Please provide more formulation details (at least 10 characters).');
      return null;
    }

    setIsLoading(true);
    setError(null);

    try {
      const classificationResult = await apiClassify(textToClassify);
      setResult(classificationResult);
      setStep(4); // Move to results step
      toast.success('Formulation successfully classified!');
      return classificationResult;
    } catch (err) {
      const msg = err.userMessage || err.message || 'Failed to classify formulation.';
      setError(msg);
      toast.error(msg);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setStep(1);
    setFormData({
      isClassical: 'no',
      herbs: '',
      intendedUse: 'dietary',
      description: '',
    });
    setResult(null);
    setError(null);
  };

  return {
    step,
    setStep,
    formData,
    updateFormData,
    result,
    isLoading,
    error,
    classify,
    reset,
    buildFullDescription,
  };
};

export default useClassification;
