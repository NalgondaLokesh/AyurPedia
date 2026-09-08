import { useEffect, useRef } from 'react';

/**
 * Reveals elements as they scroll into view.
 *
 * Attach the returned ref to any container; every descendant carrying the
 * `.reveal` class is observed once and gets `.is-visible` on entry. Motion is
 * intentionally restrained (short travel, long ease) — the CSS honours
 * `prefers-reduced-motion` by rendering everything visible up front.
 */
export const useReveal = ({ threshold = 0.16, rootMargin = '0px 0px -8% 0px' } = {}) => {
  const containerRef = useRef(null);

  useEffect(() => {
    const root = containerRef.current;
    if (!root) return;

    const targets = Array.from(root.querySelectorAll('.reveal'));
    if (targets.length === 0) return;

    // No IntersectionObserver (or reduced motion) — show everything immediately.
    const prefersReducedMotion =
      typeof window !== 'undefined' &&
      window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

    if (typeof IntersectionObserver === 'undefined' || prefersReducedMotion) {
      targets.forEach((el) => el.classList.add('is-visible'));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      },
      { threshold, rootMargin }
    );

    targets.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [threshold, rootMargin]);

  return containerRef;
};

export default useReveal;
