import React, { useState } from 'react';
import { HiSparkles, HiDocumentMagnifyingGlass, HiExclamationTriangle, HiCheckCircle, HiInformationCircle } from 'react-icons/hi2';
import api from '../../services/api';

export const PatentNoveltyChecker = () => {
  const [formData, setFormData] = useState({
    formulation_name: '',
    ingredients: '',
    process: '',
    intended_use: '',
    novelty_claim: '',
    jurisdiction: 'India'
  });
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [section3pInfo, setSection3pInfo] = useState(null);
  const [isLoadingSection3p, setIsLoadingSection3p] = useState(false);
  const [section3pError, setSection3pError] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const ingredients = formData.ingredients.split(',').map(i => i.trim()).filter(i => i);
      
      const response = await api.post('/api/patent/novelty-check', {
        ...formData,
        ingredients
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze patent novelty');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSection3pInfo = async () => {
    setIsLoadingSection3p(true);
    setSection3pError(null);
    try {
      const response = await api.get('/api/patent/section3p-info');
      setSection3pInfo(response.data);
    } catch (err) {
      console.error('Failed to fetch Section 3(p) info:', err);
      setSection3pError('Failed to load Section 3(p) information');
    } finally {
      setIsLoadingSection3p(false);
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'High': return 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400';
      case 'Medium': return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'Low': return 'text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400';
      default: return 'text-stone-600 bg-stone-50 dark:bg-stone-900/20 dark:text-stone-400';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Patentable': return 'text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400';
      case 'Partially Patentable': return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'Not Patentable': return 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400';
      case 'Uncertain': return 'text-stone-600 bg-stone-50 dark:bg-stone-900/20 dark:text-stone-400';
      default: return 'text-stone-600 bg-stone-50 dark:bg-stone-900/20 dark:text-stone-400';
    }
  };

  const getRiskIcon = (risk) => {
    switch (risk) {
      case 'High': return <HiExclamationTriangle className="w-5 h-5" />;
      case 'Medium': return <HiInformationCircle className="w-5 h-5" />;
      case 'Low': return <HiCheckCircle className="w-5 h-5" />;
      default: return <HiInformationCircle className="w-5 h-5" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-800 text-accent-300 rounded-2xl shadow-card mb-4">
          <HiDocumentMagnifyingGlass className="w-8 h-8" />
        </div>
        <h1 className="font-serif text-3xl font-semibold text-stone-900 dark:text-stone-100 mb-2">
          Patent Novelty Checker
        </h1>
        <p className="text-stone-600 dark:text-stone-400">
          Analyze Ayurvedic formulations for patent novelty and Section 3(p) compliance
        </p>
      </div>

      {/* Section 3(p) Info Toggle */}
      <div className="mb-6">
        <button
          onClick={() => {
            if (section3pInfo) {
              setSection3pInfo(null);
            } else {
              fetchSection3pInfo();
            }
          }}
          disabled={isLoadingSection3p}
          className="text-sm text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <HiInformationCircle className="w-4 h-4" />
          {isLoadingSection3p ? 'Loading...' : section3pInfo ? 'Hide Section 3(p) Information' : 'Learn about Section 3(p) of Indian Patents Act'}
        </button>
        {section3pError && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">{section3pError}</p>
        )}
        {section3pInfo && (
          <div className="mt-4 p-4 bg-stone-50 dark:bg-stone-900/40 rounded-xl border border-stone-200 dark:border-stone-800">
            <h3 className="font-semibold text-stone-900 dark:text-stone-100 mb-2">
              Section 3(p) - {section3pInfo.title}
            </h3>
            <p className="text-sm text-stone-600 dark:text-stone-400 mb-3">
              {section3pInfo.description}
            </p>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-medium text-red-600 dark:text-red-400 mb-1">Not Patentable:</h4>
                <ul className="list-disc list-inside text-stone-600 dark:text-stone-400">
                  {section3pInfo.exclusions.map((exclusion, i) => (
                    <li key={i}>{exclusion}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-green-600 dark:text-green-400 mb-1">Patentable:</h4>
                <ul className="list-disc list-inside text-stone-600 dark:text-stone-400">
                  {section3pInfo.patentable_elements.map((element, i) => (
                    <li key={i}>{element}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Form */}
      <div className="bg-[#fffdf8] dark:bg-primary-950/40 rounded-3xl p-8 shadow-card border border-stone-200/80 dark:border-primary-900/50 mb-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="formulation_name" className="block text-sm font-semibold text-stone-700 dark:text-stone-300 mb-2">
              Formulation Name *
            </label>
            <input
              type="text"
              id="formulation_name"
              name="formulation_name"
              value={formData.formulation_name}
              onChange={handleChange}
              required
              placeholder="e.g., Ashwagandha Rasayana"
              className="w-full px-4 py-3 bg-stone-50 dark:bg-primary-950/50 border border-stone-200 dark:border-primary-900/50 rounded-xl text-stone-900 dark:text-stone-100 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 transition-all"
            />
          </div>

          <div>
            <label htmlFor="ingredients" className="block text-sm font-semibold text-stone-700 dark:text-stone-300 mb-2">
              Ingredients * (comma-separated)
            </label>
            <input
              type="text"
              id="ingredients"
              name="ingredients"
              value={formData.ingredients}
              onChange={handleChange}
              required
              placeholder="e.g., Ashwagandha, Honey, Ghee, Milk"
              className="w-full px-4 py-3 bg-stone-50 dark:bg-primary-950/50 border border-stone-200 dark:border-primary-900/50 rounded-xl text-stone-900 dark:text-stone-100 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 transition-all"
            />
          </div>

          <div>
            <label htmlFor="process" className="block text-sm font-semibold text-stone-700 dark:text-stone-300 mb-2">
              Preparation Process *
            </label>
            <textarea
              id="process"
              name="process"
              value={formData.process}
              onChange={handleChange}
              required
              rows={3}
              placeholder="Describe the preparation method, any modern techniques used"
              className="w-full px-4 py-3 bg-stone-50 dark:bg-primary-950/50 border border-stone-200 dark:border-primary-900/50 rounded-xl text-stone-900 dark:text-stone-100 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 transition-all resize-none"
            />
          </div>

          <div>
            <label htmlFor="intended_use" className="block text-sm font-semibold text-stone-700 dark:text-stone-300 mb-2">
              Intended Use *
            </label>
            <input
              type="text"
              id="intended_use"
              name="intended_use"
              value={formData.intended_use}
              onChange={handleChange}
              required
              placeholder="e.g., Rejuvenation, Stress relief, Immunity booster"
              className="w-full px-4 py-3 bg-stone-50 dark:bg-primary-950/50 border border-stone-200 dark:border-primary-900/50 rounded-xl text-stone-900 dark:text-stone-100 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 transition-all"
            />
          </div>

          <div>
            <label htmlFor="novelty_claim" className="block text-sm font-semibold text-stone-700 dark:text-stone-300 mb-2">
              Novelty Claim (optional)
            </label>
            <input
              type="text"
              id="novelty_claim"
              name="novelty_claim"
              value={formData.novelty_claim}
              onChange={handleChange}
              placeholder="e.g., Enhanced bioavailability with nano-emulsion"
              className="w-full px-4 py-3 bg-stone-50 dark:bg-primary-950/50 border border-stone-200 dark:border-primary-900/50 rounded-xl text-stone-900 dark:text-stone-100 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 transition-all"
            />
          </div>

          <div>
            <label htmlFor="jurisdiction" className="block text-sm font-semibold text-stone-700 dark:text-stone-300 mb-2">
              Jurisdiction
            </label>
            <select
              id="jurisdiction"
              name="jurisdiction"
              value={formData.jurisdiction}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-stone-50 dark:bg-primary-950/50 border border-stone-200 dark:border-primary-900/50 rounded-xl text-stone-900 dark:text-stone-100 focus:outline-none focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 transition-all"
            >
              <option value="India">India</option>
              <option value="International">International</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-4 text-white btn-premium font-bold rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <HiSparkles className="w-5 h-5 text-accent-300" />
                <span>Analyze Patent Novelty</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
          <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Novelty Score */}
          <div className="bg-[#fffdf8] dark:bg-primary-950/40 rounded-3xl p-8 shadow-card border border-stone-200/80 dark:border-primary-900/50">
            <h2 className="font-serif text-2xl font-semibold text-stone-900 dark:text-stone-100 mb-6">
              Novelty Analysis Results
            </h2>

            {/* Overall Score */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-stone-700 dark:text-stone-300">
                  Overall Novelty Score
                </span>
                <span className={`text-sm font-bold px-3 py-1 rounded-full ${getRiskColor(result.risk_level)} flex items-center gap-2`}>
                  {getRiskIcon(result.risk_level)}
                  {result.risk_level} Risk
                </span>
              </div>
              <div className="relative h-4 bg-stone-200 dark:bg-stone-700 rounded-full overflow-hidden">
                <div
                  className="absolute h-full bg-gradient-to-r from-primary-600 to-accent-500 transition-all duration-500"
                  style={{ width: `${result.novelty_score}%` }}
                />
              </div>
              <div className="flex justify-between mt-1">
                <span className="text-xs text-stone-500 dark:text-stone-400">0</span>
                <span className="text-lg font-bold text-stone-900 dark:text-stone-100">
                  {result.novelty_score.toFixed(0)}/100
                </span>
                <span className="text-xs text-stone-500 dark:text-stone-400">100</span>
              </div>
            </div>

            {/* Component Breakdown */}
            <div className="space-y-4">
              <h3 className="font-semibold text-stone-900 dark:text-stone-100">Component Breakdown</h3>
              {result.component_novelty.map((component, index) => (
                <div key={index} className="p-4 bg-stone-50 dark:bg-stone-900/40 rounded-xl border border-stone-200 dark:border-stone-800">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-stone-900 dark:text-stone-100">{component.component}</span>
                    <span className={`text-sm font-bold px-2 py-1 rounded-full ${getRiskColor(component.risk_level)}`}>
                      {component.score.toFixed(0)}/100
                    </span>
                  </div>
                  <p className="text-sm text-stone-600 dark:text-stone-400 mb-2">{component.analysis}</p>
                  {component.traditional_references.length > 0 && (
                    <div className="text-xs text-stone-500 dark:text-stone-400">
                      <span className="font-medium">Traditional References:</span> {component.traditional_references.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Section 3(p) Analysis */}
          <div className="bg-[#fffdf8] dark:bg-primary-950/40 rounded-3xl p-8 shadow-card border border-stone-200/80 dark:border-primary-900/50">
            <h2 className="font-serif text-2xl font-semibold text-stone-900 dark:text-stone-100 mb-6">
              Section 3(p) Compliance Analysis
            </h2>

            <div className="mb-6">
              <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full font-bold text-lg ${getStatusColor(result.section3p_analysis.status)}`}>
                {result.section3p_analysis.status === 'Patentable' && <HiCheckCircle className="w-6 h-6" />}
                {result.section3p_analysis.status === 'Not Patentable' && <HiExclamationTriangle className="w-6 h-6" />}
                {result.section3p_analysis.status === 'Partially Patentable' && <HiInformationCircle className="w-6 h-6" />}
                {result.section3p_analysis.status}
              </div>
            </div>

            <p className="text-stone-600 dark:text-stone-400 mb-6">{result.section3p_analysis.analysis}</p>

            <div className="grid md:grid-cols-2 gap-4 mb-6">
              <div>
                <h4 className="font-semibold text-green-600 dark:text-green-400 mb-2 flex items-center gap-2">
                  <HiCheckCircle className="w-5 h-5" />
                  Patentable Elements
                </h4>
                {result.section3p_analysis.patentable_elements.length > 0 ? (
                  <ul className="space-y-1">
                    {result.section3p_analysis.patentable_elements.map((element, i) => (
                      <li key={i} className="text-sm text-stone-600 dark:text-stone-400 flex items-start gap-2">
                        <span className="text-green-500 mt-1">✓</span>
                        {element}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-stone-500 dark:text-stone-400">None identified</p>
                )}
              </div>

              <div>
                <h4 className="font-semibold text-red-600 dark:text-red-400 mb-2 flex items-center gap-2">
                  <HiExclamationTriangle className="w-5 h-5" />
                  Non-Patentable Elements
                </h4>
                {result.section3p_analysis.non_patentable_elements.length > 0 ? (
                  <ul className="space-y-1">
                    {result.section3p_analysis.non_patentable_elements.map((element, i) => (
                      <li key={i} className="text-sm text-stone-600 dark:text-stone-400 flex items-start gap-2">
                        <span className="text-red-500 mt-1">✗</span>
                        {element}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-stone-500 dark:text-stone-400">None identified</p>
                )}
              </div>
            </div>

            {result.section3p_analysis.recommendations.length > 0 && (
              <div>
                <h4 className="font-semibold text-stone-900 dark:text-stone-100 mb-2 flex items-center gap-2">
                  <HiSparkles className="w-5 h-5 text-accent-500" />
                  Recommendations
                </h4>
                <ul className="space-y-2">
                  {result.section3p_analysis.recommendations.map((recommendation, i) => (
                    <li key={i} className="text-sm text-stone-600 dark:text-stone-400 flex items-start gap-2 p-3 bg-stone-50 dark:bg-stone-900/40 rounded-lg">
                      <span className="text-accent-500 font-bold">{i + 1}.</span>
                      {recommendation}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Prior Art */}
          {result.prior_art.length > 0 && (
            <div className="bg-[#fffdf8] dark:bg-primary-950/40 rounded-3xl p-8 shadow-card border border-stone-200/80 dark:border-primary-900/50">
              <h2 className="font-serif text-2xl font-semibold text-stone-900 dark:text-stone-100 mb-6">
                Prior Art References
              </h2>
              <div className="space-y-4">
                {result.prior_art.map((art, index) => (
                  <div key={index} className="p-4 bg-stone-50 dark:bg-stone-900/40 rounded-xl border border-stone-200 dark:border-stone-800">
                    <div className="flex items-start justify-between mb-2">
                      <span className="font-medium text-stone-900 dark:text-stone-100">{art.source}</span>
                      <span className="text-xs text-stone-500 dark:text-stone-400">
                        Relevance: {(art.relevance * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-sm text-stone-600 dark:text-stone-400 mb-2">{art.description}</p>
                    <p className="text-xs text-stone-500 dark:text-stone-400 italic">{art.citation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Disclaimer */}
          <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl">
            <p className="text-sm text-amber-800 dark:text-amber-200 flex items-start gap-2">
              <HiExclamationTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              {result.disclaimer}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatentNoveltyChecker;
