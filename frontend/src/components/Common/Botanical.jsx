import React from 'react';

/**
 * Refined Ayurvedic line-art motifs used across the app in place of emoji.
 * All motifs use `currentColor` so they inherit text color for easy theming.
 */

// Brand emblem — a stylised botanical sprig within a seal.
export const AyurMark = ({ className = 'w-6 h-6' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className} aria-hidden="true">
    <path
      d="M24 39c0-9 0-15 0-20M24 39c0-9 0-15 0-20"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <path
      d="M24 19c-6-2-9-6-9-11 5 0 8 4 9 8 1-4 4-8 9-8 0 5-3 9-9 11Z"
      fill="currentColor"
      fillOpacity="0.9"
    />
    <path
      d="M24 27c-4-1.5-7-4-7.5-7.5M24 27c4-1.5 7-4 7.5-7.5"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      opacity="0.65"
    />
    <path
      d="M24 34c-3.5-1.2-6-3.2-6.5-6M24 34c3.5-1.2 6-3.2 6.5-6"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      opacity="0.5"
    />
  </svg>
);

// A single leaf / peepal-inspired form.
export const Leaf = ({ className = 'w-6 h-6' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className} aria-hidden="true">
    <path
      d="M24 6C15 13 9 21 9 31c0 7 5 11 15 11s15-4 15-11c0-10-6-18-15-25Z"
      stroke="currentColor"
      strokeWidth="2"
      fill="none"
    />
    <path d="M24 12v27" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    <path
      d="M24 20c-3-2-6-2.5-8-2.5M24 26c3-2 6-2.5 8-2.5M24 31c-3-2-6-2.5-8-2.5"
      stroke="currentColor"
      strokeWidth="1.4"
      strokeLinecap="round"
      opacity="0.7"
    />
  </svg>
);

// Decorative branching sprig for hero / section ornamentation.
export const Sprig = ({ className = 'w-24 h-24' }) => (
  <svg viewBox="0 0 120 120" fill="none" className={className} aria-hidden="true">
    <path d="M60 116V30" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    {[
      'M60 44c-10-2-18-9-20-20 11 1 18 8 20 20Z',
      'M60 44c10-2 18-9 20-20-11 1-18 8-20 20Z',
      'M60 66c-9-2-16-8-18-18 10 1 16 7 18 18Z',
      'M60 66c9-2 16-8 18-18-10 1-16 7-18 18Z',
      'M60 88c-8-2-14-7-16-16 9 1 14 6 16 16Z',
      'M60 88c8-2 14-7 16-16-9 1-14 6-16 16Z',
    ].map((d, i) => (
      <path key={i} d={d} fill="currentColor" fillOpacity={0.16 + i * 0.03} />
    ))}
    <circle cx="60" cy="24" r="4" fill="currentColor" fillOpacity="0.5" />
  </svg>
);

// Concentric mandala-style corner ornament.
export const Mandala = ({ className = 'w-64 h-64' }) => (
  <svg viewBox="0 0 200 200" fill="none" className={className} aria-hidden="true">
    <circle cx="100" cy="100" r="90" stroke="currentColor" strokeWidth="1" opacity="0.5" />
    <circle cx="100" cy="100" r="70" stroke="currentColor" strokeWidth="1" opacity="0.4" />
    <circle cx="100" cy="100" r="50" stroke="currentColor" strokeWidth="1" opacity="0.3" />
    {Array.from({ length: 12 }).map((_, i) => {
      const angle = (i * 30 * Math.PI) / 180;
      const x1 = 100 + Math.cos(angle) * 50;
      const y1 = 100 + Math.sin(angle) * 50;
      const x2 = 100 + Math.cos(angle) * 90;
      const y2 = 100 + Math.sin(angle) * 90;
      return (
        <g key={i}>
          <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="currentColor" strokeWidth="1" opacity="0.35" />
          <path
            d={`M${x1} ${y1} q${Math.cos(angle) * 14} ${Math.sin(angle) * 14} 0 28`}
            stroke="currentColor"
            strokeWidth="0.8"
            opacity="0.25"
            fill="none"
          />
        </g>
      );
    })}
  </svg>
);

// Small ornamental diamond used inside dividers / labels.
export const Diamond = ({ className = 'w-3 h-3' }) => (
  <svg viewBox="0 0 12 12" fill="none" className={className} aria-hidden="true">
    <path d="M6 0l6 6-6 6-6-6 6-6Z" fill="currentColor" />
    <path d="M6 3l3 3-3 3-3-3 3-3Z" fill="#faf8f3" fillOpacity="0.35" />
  </svg>
);

export default AyurMark;
