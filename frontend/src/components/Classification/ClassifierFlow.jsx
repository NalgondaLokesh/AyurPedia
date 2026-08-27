import React, { useState, useEffect } from 'react';
import { useClassification } from '../../hooks/useClassification';
import ClassificationQuestion from './ClassificationQuestion';
import ClassificationResult from './ClassificationResult';
import Disclaimer from '../Common/Disclaimer';
import { Mandala } from '../Common/Botanical';
import { HiDocumentMagnifyingGlass, HiSparkles, HiPencilSquare, HiListBullet, HiInformationCircle } from 'react-icons/hi2';
import api from '../../services/api';

export const ClassifierFlow = () => {
  const {
    step,
    setStep,
    formData,
    updateFormData,
    result,
    isLoading,
    error,
    classify,
    reset,
  } = useClassification();

  const [mode, setMode] = useState('wizard'); // 'wizard' | 'direct'
  const [directDescription, setDirectDescription] = useState('');
  const [explanation, setExplanation] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(true);

  // Fetch AI-powered explanation on component mount
  useEffect(() => {
    const fetchExplanation = async () => {
      try {
        const response = await api.get('/api/classify/explanation');
        setExplanation(response.data);
      } catch (error) {
        console.error('Failed to fetch classification explanation:', error);
        // Set fallback explanation
        setExplanation({
          headline: "Understanding Ayurvedic Regulatory Classification",
          explanation: "Classification determines which regulatory framework applies to your Ayurvedic formulation. Different categories have different licensing requirements, approval processes, and compliance standards.",
          key_categories: ["Classical", "Proprietary", "Ayurveda-Aahar", "Others"],
          business_impact: "Correct classification ensures proper regulatory compliance and market access."
        });
      } finally {
        setLoadingExplanation(false);
      }
    };

    fetchExplanation();
  }, []);

  const handleDirectClassify = (e) => {
    e.preventDefault();
    classify(directDescription);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
      {/* Header Banner */}
      <div className="bg-primary-900 rounded-3xl p-6 sm:p-7 text-white shadow-card relative overflow-hidden">
        <Mandala className="absolute -top-16 -right-16 w-64 h-64 text-accent-400/10 pointer-events-none" />
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="p-1.5 bg-white/10 rounded-lg text-accent-300 ring-1 ring-accent-400/20">
                <HiDocumentMagnifyingGlass className="w-5 h-5" />
              </div>
              <span className="overline text-accent-300">
                Regulatory Decision Engine
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-serif font-semibold tracking-tight">
              Ayurvedic Formulation Classifier
            </h1>
            <p className="text-xs text-stone-300 mt-2 max-w-xl leading-relaxed">
              Categorize traditional &amp; modern herbal formulations across 7 statutory classes — Classical, Proprietary, Ayurveda-Aahar, Cosmetic, Phytopharmaceutical, Nutraceutical &amp; more.
            </p>
          </div>

          {/* Mode Switcher */}
          {!result && (
            <div className="flex items-center bg-black/25 p-1 rounded-xl shrink-0 self-start sm:self-center border border-white/10">
              <button
                type="button"
                onClick={() => setMode('wizard')}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg transition-all duration-300 ${
                  mode === 'wizard' ? 'bg-stone-50 text-primary-900 shadow-sm' : 'text-stone-300 hover:text-white hover:bg-white/10'
                }`}
              >
                <HiListBullet className="w-4 h-4" />
                <span>Wizard</span>
              </button>
              <button
                type="button"
                onClick={() => setMode('direct')}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg transition-all duration-300 ${
                  mode === 'direct' ? 'bg-stone-50 text-primary-900 shadow-sm' : 'text-stone-300 hover:text-white hover:bg-white/10'
                }`}
              >
                <HiPencilSquare className="w-4 h-4" />
                <span>Quick Paste</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Classification Explanation Section */}
      <div className="bg-gradient-to-br from-stone-50 to-amber-50 dark:from-primary-950/30 dark:to-primary-900/30 rounded-3xl p-6 sm:p-7 border border-stone-200/80 dark:border-primary-900/50 shadow-sm">
        {loadingExplanation ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-500"></div>
          </div>
        ) : explanation ? (
          <div className="flex items-start gap-4">
            <div className={`p-2.5 rounded-xl shrink-0 ${explanation.ai_generated ? 'bg-accent-100 dark:bg-accent-900/30 text-accent-700 dark:text-accent-300' : 'bg-stone-200 dark:bg-stone-700 text-stone-600 dark:text-stone-300'}`}>
              {explanation.ai_generated ? <HiSparkles className="w-6 h-6" /> : <HiInformationCircle className="w-6 h-6" />}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <h3 className="text-lg font-serif font-semibold text-stone-900 dark:text-stone-100">
                  {explanation.headline}
                </h3>
                {explanation.ai_generated && (
                  <span className="text-[10px] bg-accent-100 dark:bg-accent-900/30 text-accent-700 dark:text-accent-300 px-2 py-0.5 rounded-full font-medium">
                    AI + RAG Powered
                  </span>
                )}
              </div>
              <p className="text-sm text-stone-600 dark:text-stone-300 leading-relaxed mb-3">
                {explanation.explanation}
              </p>
              
              {explanation.key_categories && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
                  {explanation.key_categories.map((category, index) => (
                    <div key={index} className="p-3 bg-white dark:bg-primary-900/50 rounded-xl border border-stone-200 dark:border-primary-800/50">
                      <div className="text-xs font-bold text-primary-800 dark:text-accent-400 mb-1">{category}</div>
                    </div>
                  ))}
                </div>
              )}
              
              {explanation.business_impact && (
                <div className="mt-4 p-3 bg-white/60 dark:bg-primary-900/30 rounded-xl border border-stone-200 dark:border-primary-800/50">
                  <div className="text-xs font-semibold text-stone-700 dark:text-stone-300 mb-1">Business Impact</div>
                  <div className="text-[11px] text-stone-600 dark:text-stone-400">{explanation.business_impact}</div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center py-4 text-stone-500 dark:text-stone-400 text-sm">
            Unable to load classification explanation
          </div>
        )}
      </div>

      {/* Main Classifier Card */}
      <div className="bg-[#fffdf8] dark:bg-primary-950/40 rounded-3xl p-6 sm:p-8 border border-stone-200/80 dark:border-primary-900/50 shadow-card transition-all duration-300">
        {result ? (
          <ClassificationResult result={result} onReset={reset} />
        ) : mode === 'wizard' ? (
          <ClassificationQuestion
            step={step}
            totalSteps={3}
            formData={formData}
            updateFormData={updateFormData}
            onNext={() => setStep((s) => Math.min(s + 1, 3))}
            onPrev={() => setStep((s) => Math.max(s - 1, 1))}
            onClassify={() => classify()}
            isLoading={isLoading}
          />
        ) : (
          /* Direct Paste Mode */
          <form onSubmit={handleDirectClassify} className="space-y-4 fade-in">
            <div>
              <label className="block text-sm font-bold text-stone-800 dark:text-stone-200 mb-1">
                Enter Formulation Composition &amp; Claims
              </label>
              <p className="text-xs text-stone-500 dark:text-stone-400 mb-2">
                Paste your product ingredients, intended benefits, textual references or extract methods.
              </p>
              <textarea
                rows="5"
                required
                value={directDescription}
                onChange={(e) => setDirectDescription(e.target.value)}
                placeholder="Example: A polyherbal chewable tablet comprising Ashwagandha (Withania somnifera) root extract 300mg, Brahmi extract 200mg, and Piperine 10mg, formulated with natural jaggery base for cognitive alertness and stress reduction."
                className="w-full p-4 text-xs sm:text-sm bg-stone-50 dark:bg-primary-950/60 border border-stone-200 dark:border-primary-900/50 rounded-2xl focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 outline-none resize-none leading-relaxed transition-all duration-300 text-stone-800 dark:text-stone-100"
              />
            </div>

            <div className="flex items-center justify-between pt-2 gap-3 flex-wrap">
              <span className="text-[11px] text-stone-400">
                Minimum 10 characters required for semantic statutory analysis.
              </span>
              <button
                type="submit"
                disabled={isLoading || directDescription.trim().length < 10}
                className="inline-flex items-center gap-2 px-6 py-2.5 text-xs font-bold text-white btn-premium disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all duration-300"
              >
                <HiSparkles className="w-4 h-4 text-accent-300" />
                <span>{isLoading ? 'Classifying...' : 'Classify Formulation'}</span>
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Legal disclaimer */}
      <Disclaimer compact={false} showEscalation={true} />
    </div>
  );
};

export default ClassifierFlow;
