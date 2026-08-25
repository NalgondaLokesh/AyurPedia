import React, { useState } from 'react';
import { useClassification } from '../../hooks/useClassification';
import ClassificationQuestion from './ClassificationQuestion';
import ClassificationResult from './ClassificationResult';
import Disclaimer from '../Common/Disclaimer';
import { HiDocumentMagnifyingGlass, HiSparkles, HiPencilSquare, HiListBullet } from 'react-icons/hi2';

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

  const handleDirectClassify = (e) => {
    e.preventDefault();
    classify(directDescription);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-primary-900 via-primary-800 to-emerald-900 rounded-3xl p-6 text-white shadow-glass relative overflow-hidden">
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <div className="p-1.5 bg-white/10 rounded-lg backdrop-blur-xs text-accent-400">
                <HiDocumentMagnifyingGlass className="w-5 h-5" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-accent-300">
                Regulatory Decision Engine
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-black tracking-tight">
              Ayurvedic Formulation Classifier
            </h1>
            <p className="text-xs text-emerald-100 mt-1 max-w-xl">
              Categorize traditional & modern herbal formulations under 7 statutory classes (Classical, Proprietary, Ayurveda-Aahar, Cosmetic, Phytopharmaceutical, Nutraceutical, Unknown).
            </p>
          </div>

          {/* Mode Switcher */}
          {!result && (
            <div className="flex items-center bg-black/20 p-1 rounded-xl backdrop-blur-xs shrink-0 self-start sm:self-center">
              <button
                type="button"
                onClick={() => setMode('wizard')}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg transition-all ${
                  mode === 'wizard' ? 'bg-white text-primary-900 shadow-xs' : 'text-emerald-200 hover:text-white'
                }`}
              >
                <HiListBullet className="w-4 h-4" />
                <span>Wizard</span>
              </button>
              <button
                type="button"
                onClick={() => setMode('direct')}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg transition-all ${
                  mode === 'direct' ? 'bg-white text-primary-900 shadow-xs' : 'text-emerald-200 hover:text-white'
                }`}
              >
                <HiPencilSquare className="w-4 h-4" />
                <span>Quick Paste</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Classifier Card */}
      <div className="bg-white/90 backdrop-blur-md rounded-3xl p-6 sm:p-8 border border-stone-200/90 shadow-glass">
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
          <form onSubmit={handleDirectClassify} className="space-y-4 animate-in fade-in duration-150">
            <div>
              <label className="block text-xs font-bold text-stone-800 mb-1">
                Enter Formulation Composition & Claims
              </label>
              <p className="text-xs text-stone-500 mb-2">
                Paste your product ingredients, intended benefits, textual references or extract methods.
              </p>
              <textarea
                rows="5"
                required
                value={directDescription}
                onChange={(e) => setDirectDescription(e.target.value)}
                placeholder="Example: A polyherbal chewable tablet comprising Ashwagandha (Withania somnifera) root extract 300mg, Brahmi extract 200mg, and Piperine 10mg, formulated with natural jaggery base for cognitive alertness and stress reduction."
                className="w-full p-4 text-xs sm:text-sm bg-stone-50 border border-stone-200 rounded-2xl focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none resize-none leading-relaxed"
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] text-stone-400">
                Minimum 10 characters required for semantic statutory analysis.
              </span>
              <button
                type="submit"
                disabled={isLoading || directDescription.trim().length < 10}
                className="inline-flex items-center gap-2 px-6 py-2.5 text-xs font-bold text-white bg-gradient-to-r from-primary-800 to-emerald-700 hover:opacity-95 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl shadow-md transition-all cursor-pointer"
              >
                <HiSparkles className="w-4 h-4 text-accent-400" />
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
