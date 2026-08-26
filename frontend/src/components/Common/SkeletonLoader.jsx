import React from 'react';

export const SkeletonLoader = ({ className = '', variant = 'default' }) => {
  const variants = {
    default: 'h-4 w-full',
    text: 'h-4 w-3/4',
    title: 'h-6 w-1/2',
    avatar: 'h-10 w-10 rounded-full',
    button: 'h-10 w-24 rounded-lg',
    card: 'h-32 w-full rounded-xl',
    chat: 'h-16 w-64 rounded-2xl',
    citation: 'h-20 w-full rounded-xl'
  };

  return (
    <div
      className={`skeleton rounded ${variants[variant] || variants.default} ${className}`}
      role="status"
      aria-label="Loading..."
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
};

export const ChatSkeleton = () => (
  <div className="flex items-start gap-3 p-4">
    <div className="w-8 h-8 rounded-xl skeleton shrink-0" />
    <div className="flex-1 space-y-2">
      <SkeletonLoader variant="title" className="w-1/3" />
      <SkeletonLoader variant="text" />
      <SkeletonLoader variant="text" />
      <SkeletonLoader variant="text" className="w-2/3" />
    </div>
  </div>
);

export const CitationSkeleton = () => (
  <div className="bg-white/90 border border-stone-200/90 rounded-xl p-3">
    <div className="flex items-start gap-2">
      <div className="w-6 h-6 rounded-lg skeleton shrink-0" />
      <div className="flex-1 space-y-2">
        <SkeletonLoader variant="text" className="w-1/2" />
        <SkeletonLoader variant="text" className="w-1/3" />
      </div>
    </div>
  </div>
);

export const ClassificationSkeleton = () => (
  <div className="space-y-4">
    <div className="h-48 rounded-3xl skeleton" />
    <div className="h-24 rounded-2xl skeleton" />
    <div className="flex gap-2">
      <div className="h-10 flex-1 rounded-xl skeleton" />
      <div className="h-10 flex-1 rounded-xl skeleton" />
    </div>
  </div>
);

export default SkeletonLoader;
