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
// 2. Active nav link highlighting, synced to scroll position
// ==========================================================
const navLinks = document.querySelectorAll('.topnav__links a');
const trackedSections = document.querySelectorAll('[id]');

const navObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    const id = entry.target.getAttribute('id');
    navLinks.forEach(link => {
      link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
    });
  });
}, { rootMargin: '-45% 0px -50% 0px' });

trackedSections.forEach(section => navObserver.observe(section));

// ==========================================================
// 3. Elevate top nav with a shadow once the page is scrolled
// ==========================================================
const topnav = document.getElementById('topnav');

const updateNavShadow = () => {
  topnav.classList.toggle('is-scrolled', window.scrollY > 12);
};
updateNavShadow();
window.addEventListener('scroll', updateNavShadow, { passive: true });

// ==========================================================
// 4. Smooth-scroll anchor links, offset for the sticky nav
// ==========================================================
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', (e) => {
    const targetId = link.getAttribute('href').slice(1);
    const target = document.getElementById(targetId);
    if (!target) return;

    e.preventDefault();
    const navHeight = topnav.offsetHeight;
    const top = target.getBoundingClientRect().top + window.scrollY - navHeight - 12;
    window.scrollTo({ top, behavior: 'smooth' });

    // Close the mobile burger menu after choosing a section
    closeBurgerMenu();
  });
});

// ==========================================================
// 5. Burger menu — show/hide the mobile nav via JavaScript
// ==========================================================
const burgerBtn = document.getElementById('burgerBtn');
const navLinksWrap = document.getElementById('navLinks');

function openBurgerMenu() {
  navLinksWrap.classList.add('is-open');
  burgerBtn.classList.add('is-open');
  burgerBtn.setAttribute('aria-expanded', 'true');
}

function closeBurgerMenu() {
  navLinksWrap.classList.remove('is-open');
  burgerBtn.classList.remove('is-open');
  burgerBtn.setAttribute('aria-expanded', 'false');
}

burgerBtn.addEventListener('click', () => {
  const isOpen = navLinksWrap.classList.contains('is-open');
  isOpen ? closeBurgerMenu() : openBurgerMenu();
});

// Close the menu if the viewport is resized back to desktop width
window.addEventListener('resize', () => {
  if (window.innerWidth > 760) closeBurgerMenu();
});

// ==========================================================
// 6. Carousel — projects
// ==========================================================
const track = document.getElementById('carouselTrack');
const slides = Array.from(track.children);
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const dotsWrap = document.getElementById('carouselDots');
const countLabel = document.getElementById('carouselCount');

let currentSlide = 0;

// Build one dot per slide
slides.forEach((_, i) => {
  const dot = document.createElement('button');
  dot.setAttribute('aria-label', `ไปยังโปรเจกต์ที่ ${i + 1}`);
  if (i === 0) dot.classList.add('active');
  dot.addEventListener('click', () => goToSlide(i));
  dotsWrap.appendChild(dot);
});
const dots = Array.from(dotsWrap.children);

function pad(n) {
  return String(n).padStart(2, '0');
}

function goToSlide(index) {
  currentSlide = (index + slides.length) % slides.length;
  track.style.transform = `translateX(-${currentSlide * 100}%)`;
  dots.forEach((dot, i) => dot.classList.toggle('active', i === currentSlide));
  countLabel.textContent = `${pad(currentSlide + 1)} / ${pad(slides.length)}`;
}
goToSlide(0);

prevBtn.addEventListener('click', () => goToSlide(currentSlide - 1));
nextBtn.addEventListener('click', () => goToSlide(currentSlide + 1));

// Optional: auto-advance every 6 seconds, pausing while the user interacts
let carouselTimer = setInterval(() => goToSlide(currentSlide + 1), 6000);
const carouselEl = document.getElementById('projectCarousel');
carouselEl.addEventListener('mouseenter', () => clearInterval(carouselTimer));
carouselEl.addEventListener('mouseleave', () => {
  carouselTimer = setInterval(() => goToSlide(currentSlide + 1), 6000);
});

// ==========================================================
// 7. Contact form — HTML pattern validation + JS sanitization
// ==========================================================
const contactForm = document.getElementById('contactForm');
const formStatus = document.getElementById('formStatus');

// Mark a field as "touched" once the user leaves it, so the
// :invalid.touched CSS rule only shows red after a real attempt.
contactForm.querySelectorAll('input, textarea').forEach(field => {
  field.addEventListener('blur', () => field.classList.add('touched'));
});

// Strip anything that looks like HTML/script and trim whitespace,
// so user input can never inject markup if it is echoed back later.
function sanitizeInput(value) {
  return value
    .replace(/<[^>]*>/g, '')   // remove HTML tags
    .replace(/[<>]/g, '')      // remove any stray angle brackets
    .trim();
}

// This object holds the sanitized values for later use
// (e.g. sending to a backend, logging, or displaying elsewhere).
let contactSubmission = null;

contactForm.addEventListener('submit', (e) => {
  e.preventDefault();

  // 1) Native HTML validation (type, required, pattern, minlength, maxlength)
  if (!contactForm.checkValidity()) {
    contactForm.querySelectorAll('input, textarea').forEach(field => field.classList.add('touched'));
    contactForm.reportValidity();
    formStatus.textContent = 'กรุณากรอกข้อมูลให้ถูกต้องตามรูปแบบที่กำหนด';
    formStatus.classList.add('is-error');
    return;
  }

  // 2) Read raw values from the form
  const rawName    = document.getElementById('cf-name').value;
  const rawEmail   = document.getElementById('cf-email').value;
  const rawPhone   = document.getElementById('cf-phone').value;
  const rawMessage = document.getElementById('cf-message').value;

  // 3) Sanitize before storing/using them anywhere
  contactSubmission = {
    name: sanitizeInput(rawName),
    email: sanitizeInput(rawEmail),
    phone: sanitizeInput(rawPhone),
    message: sanitizeInput(rawMessage),
    submittedAt: new Date().toISOString()
  };

  // Stored in the `contactSubmission` variable above for future use
  // (e.g. wiring up to an API call). Logged here so it's easy to verify.
  console.log('Contact form submission (sanitized):', contactSubmission);

  formStatus.classList.remove('is-error');
  formStatus.textContent = `✓ ขอบคุณ ${contactSubmission.name} ข้อความของคุณถูกบันทึกแล้ว`;
  contactForm.reset();
  contactForm.querySelectorAll('input, textarea').forEach(field => field.classList.remove('touched'));
});

// ==========================================================
// 8. Visitor counter (persisted with localStorage)
// ==========================================================
const visitorCountEl = document.getElementById('visitorCount');

function updateVisitorCount() {
  const key = 'cvVisitorCount';
  const current = parseInt(localStorage.getItem(key) || '0', 10);
  const next = current + 1;
  localStorage.setItem(key, String(next));
  visitorCountEl.textContent = next.toLocaleString();
}
updateVisitorCount();

// ==========================================================
// 9. Go to top floating button
// ==========================================================
const toTopBtn = document.getElementById('toTopBtn');

const updateToTopVisibility = () => {
  toTopBtn.classList.toggle('is-visible', window.scrollY > 400);
};
updateToTopVisibility();
window.addEventListener('scroll', updateToTopVisibility, { passive: true });

toTopBtn.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ==========================================================
// 10. Keep the footer year current automatically
// ==========================================================
const yearEl = document.getElementById('year');
if (yearEl) {
  yearEl.textContent = new Date().getFullYear();
}

// ==========================================================
// 11. Print / Save as PDF
// ==========================================================
document.getElementById('printBtn').addEventListener('click', () => {
  window.print();
});
