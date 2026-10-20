// Without this class the phone menu stays open, so the page works with JS off.
document.documentElement.classList.add('js');

function initMenu() {
  const toggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('site-nav');
  if (!toggle || !nav) return;

  const setOpen = (open) => {
    nav.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
  };
  toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
  nav.addEventListener('click', (e) => { if (e.target.closest('a')) setOpen(false); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      setOpen(false);
      toggle.focus();
    }
  });
}

function initActiveNav() {
  const links = new Map(
    [...document.querySelectorAll('#site-nav a')].map((a) => [a.getAttribute('href').slice(1), a])
  );
  const mark = (id) => links.forEach((a, key) => {
    if (key === id) a.setAttribute('aria-current', 'true');
    else a.removeAttribute('aria-current');
  });
  // A section counts as current once it crosses the upper third of the viewport.
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => { if (entry.isIntersecting) mark(entry.target.id); });
  }, { rootMargin: '-30% 0px -65% 0px' });
  links.forEach((_, id) => {
    const section = document.getElementById(id);
    if (section) observer.observe(section);
  });
}

function initTilt() {
  const finePointer = window.matchMedia('(pointer: fine)').matches;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!finePointer || reducedMotion) return;

  const maxDeg = 2;
  document.querySelectorAll('#experience .card, #projects .card').forEach((card) => {
    card.addEventListener('pointermove', (e) => {
      const r = card.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      // Signs make the edge nearest the cursor lift toward the viewer.
      card.style.transform = `perspective(600px) rotateY(${-x * maxDeg * 2}deg) rotateX(${y * maxDeg * 2}deg)`;
    });
    card.addEventListener('pointerleave', () => { card.style.transform = ''; });
  });
}

function initTheme() {
  const toggle = document.getElementById('theme-toggle');
  if (!toggle) return;
  const root = document.documentElement;
  const systemDark = window.matchMedia('(prefers-color-scheme: dark)');
  // No saved choice means the system setting decides; the head script applies a saved one before paint.
  const isDark = () => (root.dataset.theme || (systemDark.matches ? 'dark' : 'light')) === 'dark';
  const sync = () => toggle.setAttribute('aria-checked', String(isDark()));

  toggle.hidden = false;
  sync();
  toggle.addEventListener('click', () => {
    root.dataset.theme = isDark() ? 'light' : 'dark';
    try { localStorage.setItem('theme', root.dataset.theme); } catch (e) { /* private mode: choice lasts this visit only */ }
    sync();
  });
  systemDark.addEventListener('change', sync);
}

initMenu();
initActiveNav();
initTilt();
initTheme();
