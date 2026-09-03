// ==========================================================
// 1. Reveal sections on scroll
// ==========================================================
const sections = document.querySelectorAll('.section');

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in-view');

      // If this is the languages section, animate the bars once
      const bars = entry.target.querySelectorAll('.langbar__fill');
      bars.forEach(bar => {
        const target = bar.getAttribute('data-fill');
        bar.style.width = target + '%';
      });
    }
  });
}, { threshold: 0.2 });

sections.forEach(section => revealObserver.observe(section));

// ==========================================================
// 2. Print / Save as PDF
// ==========================================================
document.getElementById('printBtn').addEventListener('click', () => {
  window.print();
});