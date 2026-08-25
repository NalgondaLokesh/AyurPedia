import React from 'react';
import { HiCheckCircle, HiExclamationTriangle, HiInformationCircle } from 'react-icons/hi2';

export const ConfidenceBadge = ({ confidence = 'Medium', score = null }) => {
  const confNormalized = (confidence || 'Medium').toLowerCase();

  let config = {
    bg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    dot: 'bg-emerald-500',
    icon: HiCheckCircle,
    label: 'High confidence',
    desc: 'Verified legal sources with high semantic match',
  };

  if (confNormalized.includes('med')) {
    config = {
      bg: 'bg-amber-50 text-amber-800 border-amber-200',
      dot: 'bg-amber-500',
      icon: HiInformationCircle,
      label: 'Medium confidence',
      desc: 'Moderate source match - verify cited sections',
    };
  } else if (confNormalized.includes('low') || confNormalized.includes('un')) {
    config = {
      bg: 'bg-rose-50 text-rose-800 border-rose-200',
      dot: 'bg-rose-500',
      icon: HiExclamationTriangle,
      label: 'Low confidence',
      desc: 'Limited direct source match - legal consultation advised',
    };
  }

  const IconComponent = config.icon;

  return (
    <div
      title={config.desc}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${config.bg} shadow-2xs transition-transform hover:scale-105`}
    >
      <IconComponent className="w-3.5 h-3.5 shrink-0" />
      <span>{config.label}</span>
      {score !== null && (
        <span className="opacity-75 font-mono text-[10px]">
          ({Math.round(score * 100)}%)
        </span>
      )}
    </div>
  );
};

export default ConfidenceBadge;
