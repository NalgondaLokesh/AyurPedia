import React from 'react';
import { HiArrowLeft, HiArrowRight, HiSparkles, HiCheck, HiBookOpen, HiBeaker, HiHeart, HiCube } from 'react-icons/hi2';
import { Leaf } from '../Common/Botanical';

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

  const optionBase = 'p-4 rounded-2xl border text-left transition-all cursor-pointer';
  const optionActive = 'border-primary-600 bg-primary-50 dark:bg-primary-900/40 ring-1 ring-accent-400/40 dark:border-primary-500';
  const optionIdle = 'border-stone-200 dark:border-primary-900/50 bg-white dark:bg-primary-950/30 hover:border-accent-300 dark:hover:border-primary-700';

  return (
    <div className="space-y-6 fade-in">
      {/* Progress Bar */}
      <div>
        <div className="flex items-center justify-between text-xs text-stone-500 dark:text-stone-400 font-bold mb-1.5">
          <span>Step {step} of {totalSteps}</span>
          <span className="text-primary-700 dark:text-accent-300 font-semibold">{Math.round((step / totalSteps) * 100)}% Complete</span>
        </div>
        <div className="w-full bg-stone-200 dark:bg-primary-900/50 h-2 rounded-full overflow-hidden">
          <div
            className="bg-primary-700 h-full transition-all duration-500 rounded-full relative"
            style={{ width: `${(step / totalSteps) * 100}%` }}
          >
            <span className="absolute right-0 top-0 h-full w-1 bg-accent-400/70" />
          </div>
        </div>
      </div>

      {/* Step 1: Classical vs Proprietary */}
      {step === 1 && (
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-serif font-semibold text-stone-900 dark:text-stone-100 mb-1">
              Is this formulation from authoritative Classical Ayurvedic texts?
            </h3>
            <p className="text-xs text-stone-500 dark:text-stone-400">
              Reference texts listed in Schedule 1 of the Drugs &amp; Cosmetics Act (e.g. Charaka Samhita, Sushruta Samhita, Ayurvedic Formulary of India).
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <button
              type="button"
              onClick={() => updateFormData('isClassical', 'yes')}
              className={`${optionBase} ${formData.isClassical === 'yes' ? optionActive : optionIdle}`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-bold text-sm text-stone-900 dark:text-stone-100">Yes — Classical Text</span>
                <HiBookOpen className="w-5 h-5 text-accent-600 dark:text-accent-400" />
              </div>
              <p className="text-xs text-stone-600 dark:text-stone-400">
                Adheres to traditional textual recipes (e.g., Chyawanprash, Triphala Churna). Protected against direct patents under Section 3(p).
              </p>
            </button>

            <button
              type="button"
              onClick={() => updateFormData('isClassical', 'no')}
              className={`${optionBase} ${formData.isClassical === 'no' ? optionActive : optionIdle}`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-bold text-sm text-stone-900 dark:text-stone-100">No — New / Proprietary</span>
                <HiBeaker className="w-5 h-5 text-accent-600 dark:text-accent-400" />
              </div>
              <p className="text-xs text-stone-600 dark:text-stone-400">
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
            <h3 className="text-lg font-serif font-semibold text-stone-900 dark:text-stone-100 mb-1">
              What herbs and ingredients are included?
            </h3>
            <p className="text-xs text-stone-500 dark:text-stone-400">
              Select common Ayurvedic botanicals or type your full formulation ingredient list below.
            </p>
          </div>

          <div>
            <label className="block text-[11px] font-bold text-stone-700 dark:text-stone-300 mb-2 uppercase tracking-[0.12em]">
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
                    className={`inline-flex items-center gap-1 px-3 py-1.5 text-xs rounded-xl font-medium transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-primary-800 text-white shadow-sm'
                        : 'bg-white dark:bg-primary-950/40 hover:bg-stone-100 dark:hover:bg-primary-900/40 text-stone-700 dark:text-stone-300 border border-stone-200 dark:border-primary-900/50'
                    }`}
                  >
                    {isSelected && <HiCheck className="w-3.5 h-3.5 text-accent-300" />}
                    {herb}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-stone-700 dark:text-stone-300 mb-1">
              Specified Ingredients &amp; Proportions
            </label>
            <input
              type="text"
              value={formData.herbs}
              onChange={(e) => updateFormData('herbs', e.target.value)}
              placeholder="e.g. Ashwagandha extract 500mg, Piperine 5mg, Curcumin 250mg"
              className="w-full px-3.5 py-2.5 text-xs bg-white dark:bg-primary-950/50 border border-stone-200 dark:border-primary-900/50 rounded-xl focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 outline-none text-stone-800 dark:text-stone-100"
            />
          </div>
        </div>
      )}

      {/* Step 3: Intended Use */}
      {step === 3 && (
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-serif font-semibold text-stone-900 dark:text-stone-100 mb-1">
              What is the primary intended use &amp; delivery route?
            </h3>
            <p className="text-xs text-stone-500 dark:text-stone-400">
              Determines applicable regulatory statutes (FSSAI Food safety vs AYUSH Licensing vs Drugs &amp; Cosmetics).
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            {[
              { id: 'dietary', title: 'Dietary / Food Supplement', desc: 'Food products containing Schedule A herbs for general wellness (Ayurveda-Aahar)', Icon: HiCube },
              { id: 'medicinal', title: 'Therapeutic / Medicinal', desc: 'Intended to treat, mitigate, or cure specific pathological disease conditions', Icon: HiHeart },
              { id: 'cosmetic', title: 'Cosmetic / Topical', desc: 'Skin, hair, or topical wellness applications without systemic therapeutic claims', Icon: Leaf },
              { id: 'phytopharmaceutical', title: 'Standardized Phytopharmaceutical', desc: 'Purified botanical fraction with standardized active markers & clinical endpoints', Icon: HiBeaker },
            ].map(({ id, title, desc, Icon }) => (
              <button
                key={id}
                type="button"
                onClick={() => updateFormData('intendedUse', id)}
                className={`${optionBase} ${formData.intendedUse === id ? optionActive : optionIdle}`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-sm text-stone-900 dark:text-stone-100">{title}</span>
                  <Icon className="w-5 h-5 text-accent-600 dark:text-accent-400 shrink-0" />
                </div>
                <p className="text-xs text-stone-600 dark:text-stone-400">{desc}</p>
              </button>
            ))}
          </div>

          <div>
            <label className="block text-xs font-bold text-stone-700 dark:text-stone-300 mb-1">
              Optional Additional Formulation Description / Claims
            </label>
            <textarea
              rows="2"
              value={formData.description}
              onChange={(e) => updateFormData('description', e.target.value)}
              placeholder="e.g. A synergistic aqueous extraction of Ashwagandha and Brahmi in tablet form intended to reduce stress and improve cognitive memory."
              className="w-full px-3.5 py-2 text-xs bg-white dark:bg-primary-950/50 border border-stone-200 dark:border-primary-900/50 rounded-xl focus:ring-2 focus:ring-accent-400/25 focus:border-primary-500 outline-none resize-none text-stone-800 dark:text-stone-100"
            />
          </div>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-stone-200 dark:border-primary-900/50">
        {step > 1 ? (
          <button
            type="button"
            onClick={onPrev}
            disabled={isLoading}
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-stone-600 dark:text-stone-300 hover:text-stone-900 dark:hover:text-stone-100 hover:bg-stone-100 dark:hover:bg-primary-900/40 rounded-xl transition-all cursor-pointer"
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
            className="inline-flex items-center gap-1.5 px-5 py-2 text-xs font-bold text-white btn-premium rounded-xl transition-all cursor-pointer"
          >
            <span>Next Step</span>
            <HiArrowRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            type="button"
            onClick={onClassify}
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-6 py-2.5 text-xs font-bold text-white btn-premium rounded-xl transition-all cursor-pointer disabled:opacity-60"
          >
            <HiSparkles className="w-4 h-4 text-accent-300" />
            <span>{isLoading ? 'Classifying with AI...' : 'Run Regulatory Classification'}</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default ClassificationQuestion;
