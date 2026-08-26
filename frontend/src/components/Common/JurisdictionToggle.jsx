import React from 'react';
import { useApp } from '../../context/AppContext';
import { useChatContext } from '../../context/ChatContext';

export const JurisdictionToggle = () => {
  const { jurisdiction, setJurisdiction } = useApp();
  const { isLoading } = useChatContext();

  const options = [
    { id: 'India', label: 'India', flag: '🇮🇳', desc: 'Patents Act, BD Act, TKDL, FSSAI' },
    { id: 'International', label: 'International', flag: '🌍', desc: 'WIPO GRATK Treaty, Nagoya Protocol' },
    { id: 'Both', label: 'All Jurisdictions', flag: '🌐', desc: 'Global & Indian Legal Frameworks' },
  ];

  return (
    <div className="inline-flex items-center p-1 bg-stone-100/90 dark:bg-primary-950/50 rounded-xl border border-stone-200/80 dark:border-primary-900/50">
      {options.map((opt) => {
        const isActive = jurisdiction === opt.id;
        return (
          <button
            key={opt.id}
            type="button"
            disabled={isLoading}
            onClick={() => setJurisdiction(opt.id)}
            title={opt.desc}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all duration-200 ${
              isActive
                ? 'bg-primary-800 text-white shadow-sm'
                : 'text-stone-600 dark:text-stone-300 hover:text-stone-900 dark:hover:text-white hover:bg-white/70 dark:hover:bg-primary-900/40'
            } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <span className="text-sm">{opt.flag}</span>
            <span className="hidden sm:inline">{opt.label}</span>
          </button>
        );
      })}
    </div>
  );
};

export default JurisdictionToggle;
