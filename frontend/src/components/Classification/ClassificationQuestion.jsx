import React from 'react';
import { HiArrowLeft, HiArrowRight, HiSparkles } from 'react-icons/hi2';

export const ClassificationQuestion = ({
  step,
  totalSteps = 4,
  formData,
  updateFormData,
  onNext,
  onPrev,
  onClassify,
  isLoading,
}) => {
  const POPULAR_HERBS = [
    'Ashwagandha', 'Turmeric (Haridra)', 'Triphala', 'Brahmi', 'Neem', 
    'Tulsi', 'Guduchi', 'Shatavari', 'Amla', 'Guggulu', 'Shilajit', 'Licorice (Yashtimadhu)'
  ];

  const toggleHerb = (herb) => {
    const currentHerbs = formData.herbs ? formData.herbs.split(',').map((h) => h.trim()) : [];
    let updated;
    if (currentHerbs.includes(herb)) {
      updated = currentHerbs.filter((h) => h !== herb);
    } else {
      updated = [...currentHerbs, herb];
    }
    updateFormData('herbs', updated.join(', '));
  };

  const selectedHerbList = formData.herbs ? formData.herbs.split(',').map((h) => h.trim()) : [];

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Progress Bar */}
      <div>
        <div className="flex items-center justify-between text-xs text-stone-500 font-bold mb-1.5">
          <span>Step {step} of {totalSteps}</span>
          <span className="text-primary-700 font-semibold">{Math.round((step / totalSteps) * 100)}% Complete</span>
        </div>
        <div className="w-full bg-stone-200 h-2 rounded-full overflow-hidden">
          <div
            className="bg-gradient-to-r from-primary-600 to-herbal-leaf h-full transition-all duration-300 rounded-full"
            style={{ width: `${(step / totalSteps) * 100}%` }}
          />
        </div>
      </div>

      {/* Step 1: Classical vs Proprietary */}
      {step === 1 && (
        <div className="space-y-4">
          <div>
            <h3 className="text-base font-bold text-stone-900 mb-1">
              1. Is this formulation from authoritative Classical Ayurvedic texts?
            </h3>
            <p className="text-xs text-stone-500">
              Reference texts listed in Schedule 1 of the Drugs & Cosmetics Act (e.g. Charaka Samhita, Sushruta Samhita, Ayurvedic Formulary of India).
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <button
              type="button"
              onClick={() => updateFormData('isClassical', 'yes')}
              className={`p-4 rounded-2xl border text-left transition-all cursor-pointer ${
                formData.isClassical === 'yes'
                  ? 'border-primary-600 bg-primary-50/80 ring-2 ring-primary-500/20'
                  : 'border-stone-200 bg-white hover:border-stone-300'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-bold text-sm text-stone-900">Yes (Classical Text)</span>
                <span className="text-xl">📜</span>
              </div>
              <p className="text-xs text-stone-600">
                Formulation strictly adheres to traditional textual recipes (e.g., Chyawanprash, Triphala Churna). Protected against direct patents under Section 3(p).
              </p>
            </button>

            <button
              type="button"
              onClick={() => updateFormData('isClassical', 'no')}
              className={`p-4 rounded-2xl border text-left transition-all cursor-pointer ${
                formData.isClassical === 'no'
                  ? 'border-primary-600 bg-primary-50/80 ring-2 ring-primary-500/20'
                  : 'border-stone-200 bg-white hover:border-stone-300'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-bold text-sm text-stone-900">No (New / Proprietary Recipe)</span>
                <span className="text-xl">🧪</span>
              </div>
              <p className="text-xs text-stone-600">
                Novel combination, modern extraction, dietary food, or synergistic proprietary formulation with potential IP / patent claims.
              </p>
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Ingredients */}
      {step === 2 && (
        <div className="space-y-4">
          <div>
            <h3 className="text-base font-bold text-stone-900 mb-1">
              2. What herbs and ingredients are included?
            </h3>
            <p className="text-xs text-stone-500">
              Select common Ayurvedic botanicals or type your full formulation ingredient list below.
            </p>
          </div>

          <div>
            <label className="block text-xs font-bold text-stone-700 mb-2 uppercase tracking-wider">
              Quick Botanical Chips
            </label>
            <div className="flex flex-wrap gap-1.5">
              {POPULAR_HERBS.map((herb) => {
                const isSelected = selectedHerbList.includes(herb);
                return (
                  <button
                    key={herb}
                    type="button"
                    onClick={() => toggleHerb(herb)}
                    className={`px-3 py-1.5 text-xs rounded-xl font-medium transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-primary-700 text-white shadow-xs'
                        : 'bg-white hover:bg-stone-100 text-stone-700 border border-stone-200'
                    }`}
                  >
                    {isSelected ? '✓ ' : '+ '}
                    {herb}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-stone-700 mb-1">
              Specified Ingredients & Proportions
            </label>
            <input
              type="text"
              value={formData.herbs}
              onChange={(e) => updateFormData('herbs', e.target.value)}
              placeholder="e.g. Ashwagandha extract 500mg, Piperine 5mg, Curcumin 250mg"
              className="w-full px-3.5 py-2.5 text-xs bg-white border border-stone-200 rounded-xl focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none"
            />
          </div>
        </div>
      )}

      {/* Step 3: Intended Use */}
      {step === 3 && (
        <div className="space-y-4">
          <div>
            <h3 className="text-base font-bold text-stone-900 mb-1">
              3. What is the primary intended use & delivery route?
            </h3>
            <p className="text-xs text-stone-500">
              Determines applicable regulatory statutes (FSSAI Food safety vs AYUSH Licensing vs Drugs & Cosmetics).
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            {[
              {
                id: 'dietary',
                title: 'Dietary / Food Supplement',
                desc: 'Food products containing Schedule A herbs for general wellness (Ayurveda-Aahar)',
                icon: '🥣',
              },
              {
                id: 'medicinal',
                title: 'Therapeutic / Medicinal Treatment',
                desc: 'Intended to treat, mitigate, or cure specific pathological disease conditions',
                icon: '💊',
              },
              {
                id: 'cosmetic',
                title: 'Cosmetic / Topical Application',
                desc: 'Skin, hair, or topical wellness applications without systemic therapeutic claims',
                icon: '🌿',
              },
              {
                id: 'phytopharmaceutical',
                title: 'Standardized Phytopharmaceutical',
                desc: 'Purified botanical fraction with standardized active markers & clinical trial endpoints',
                icon: '🔬',
              },
            ].map((option) => (
              <button
                key={option.id}
                type="button"
                onClick={() => updateFormData('intendedUse', option.id)}
                className={`p-4 rounded-2xl border text-left transition-all cursor-pointer ${
                  formData.intendedUse === option.id
                    ? 'border-primary-600 bg-primary-50/80 ring-2 ring-primary-500/20'
                    : 'border-stone-200 bg-white hover:border-stone-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-sm text-stone-900">{option.title}</span>
                  <span className="text-lg">{option.icon}</span>
                </div>
                <p className="text-xs text-stone-600">{option.desc}</p>
              </button>
            ))}
          </div>

          <div>
            <label className="block text-xs font-bold text-stone-700 mb-1">
              Optional Additional Formulation Description / Claims
            </label>
            <textarea
              rows="2"
              value={formData.description}
              onChange={(e) => updateFormData('description', e.target.value)}
              placeholder="e.g. A synergistic aqueous extraction of Ashwagandha and Brahmi in tablet form intended to reduce stress and improve cognitive memory."
              className="w-full px-3.5 py-2 text-xs bg-white border border-stone-200 rounded-xl focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none resize-none"
            />
          </div>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-stone-200">
        {step > 1 ? (
          <button
            type="button"
            onClick={onPrev}
            disabled={isLoading}
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-stone-600 hover:text-stone-900 hover:bg-stone-100 rounded-xl transition-all cursor-pointer"
          >
            <HiArrowLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>
        ) : (
          <div></div>
        )}

        {step < 3 ? (
          <button
            type="button"
            onClick={onNext}
            className="inline-flex items-center gap-1.5 px-5 py-2 text-xs font-bold text-white bg-primary-700 hover:bg-primary-800 active:scale-95 rounded-xl shadow-sm transition-all cursor-pointer"
          >
            <span>Next Step</span>
            <HiArrowRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            type="button"
            onClick={onClassify}
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-6 py-2.5 text-xs font-bold text-white bg-gradient-to-r from-primary-800 to-emerald-700 hover:opacity-95 active:scale-95 rounded-xl shadow-md transition-all cursor-pointer"
          >
            <HiSparkles className="w-4 h-4 text-accent-400" />
            <span>{isLoading ? 'Classifying with AI...' : 'Run Regulatory Classification'}</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default ClassificationQuestion;
