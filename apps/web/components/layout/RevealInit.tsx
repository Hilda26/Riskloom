"use client";

import { useEffect } from "react";

// Ports the original riskloom-final.html IntersectionObserver behavior:
// any element with class "reveal" fades/slides in once it scrolls into
// view, with a slight stagger across sibling reveal elements.
export function RevealInit() {
  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("on");
            obs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08 },
    );

    const elements = document.querySelectorAll(".reveal");
    elements.forEach((el) => {
      const parent = el.parentElement;
      if (parent) {
        const sibs = parent.querySelectorAll(".reveal");
        if (sibs.length > 1) {
          const idx = Array.from(sibs).indexOf(el);
          (el as HTMLElement).style.transitionDelay = `${idx * 0.09}s`;
        }
      }
      obs.observe(el);
    });

    return () => obs.disconnect();
  }, []);

  return null;
}
