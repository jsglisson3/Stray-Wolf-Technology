/* Stray Wolf Technology. Small, plain script: the menu, the reveals, the work carousel and the intake form.
   Everything on the page works without it; this only adds the moving parts. */
(() => {
  'use strict';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');

  /* ---- The phone menu --------------------------------------------------------------- */
  const toggle = document.querySelector('[data-menu-toggle]');
  const nav = document.getElementById('site-nav');
  if (toggle && nav) {
    const label = toggle.querySelector('[data-menu-label]');
    const setOpen = (open) => {
      toggle.setAttribute('aria-expanded', String(open));
      document.body.classList.toggle('menu-open', open);
      if (label) label.textContent = open ? 'Close' : 'Menu';
    };
    toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && document.body.classList.contains('menu-open')) { setOpen(false); toggle.focus(); } });
    nav.addEventListener('click', (e) => { if (e.target.closest('a')) setOpen(false); });
    matchMedia('(min-width: 48em)').addEventListener('change', (m) => { if (m.matches) setOpen(false); });
  }

  /* ---- Reveal once, when a block enters the screen ---------------------------------- */
  const targets = document.querySelectorAll('[data-reveal]');
  if (targets.length) {
    if (!('IntersectionObserver' in window)) targets.forEach((el) => el.classList.add('is-in'));
    else {
      const io = new IntersectionObserver((entries) => {
        for (const entry of entries) { if (!entry.isIntersecting) continue; entry.target.classList.add('is-in'); io.unobserve(entry.target); }
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
      targets.forEach((el) => io.observe(el));
      // safety net: anything still hidden a while after load is shown
      window.addEventListener('load', () => setTimeout(() => {
        targets.forEach((el) => { const r = el.getBoundingClientRect(); if (r.top < innerHeight && r.bottom > 0) el.classList.add('is-in'); });
      }, 2500));
    }
  }

  /* ---- The work carousel: a scroll-snap row, with buttons for mouse and keyboard ------ */
  document.querySelectorAll('[data-carousel]').forEach((car) => {
    const track = car.querySelector('[data-track]');
    const prev = car.querySelector('[data-prev]');
    const next = car.querySelector('[data-next]');
    if (!track || !prev || !next) return;
    const slides = Array.from(track.children);
    slides.forEach((s, i) => { s.setAttribute('aria-roledescription', 'slide'); s.setAttribute('aria-label', `${i + 1} of ${slides.length}`); });
    track.setAttribute('aria-roledescription', 'carousel');
    const step = () => (slides[0] ? slides[0].getBoundingClientRect().width + (parseFloat(getComputedStyle(track).columnGap) || 0) : track.clientWidth);
    const update = () => {
      const max = track.scrollWidth - track.clientWidth - 2;
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft >= max;
    };
    const go = (dir) => track.scrollBy({ left: dir * step(), behavior: reduce.matches ? 'auto' : 'smooth' });
    prev.addEventListener('click', () => go(-1));
    next.addEventListener('click', () => go(1));
    track.addEventListener('scroll', update, { passive: true });
    track.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight') { e.preventDefault(); go(1); } if (e.key === 'ArrowLeft') { e.preventDefault(); go(-1); } });
    window.addEventListener('resize', update);
    update();
  });

  /* ---- The intake form: a plain check, then Web3Forms or a pre-filled email ---------- */
  const params = new URLSearchParams(location.search);
  const carried = (params.get('business') || '').trim().slice(0, 80);
  const intake = document.querySelector('[data-intake]');
  if (intake) {
    const business = intake.querySelector('[name="business_name"]');
    if (business && carried && !business.value) business.value = carried;
    const summary = intake.querySelector('[data-error-summary]');
    const status = intake.querySelector('[data-form-status]');
    const key = (intake.querySelector('[data-access-key]') || {}).value || '';
    const fallback = intake.dataset.fallbackEmail || '';
    const labelFor = (el) => {
      const l = intake.querySelector(`label[for="${el.id}"]`);
      return l ? l.textContent.replace(/\s*\((required|optional)\)\s*/i, '').trim() : el.name;
    };
    const check = () => {
      const bad = [];
      intake.querySelectorAll('[required]').forEach((el) => {
        el.removeAttribute('aria-invalid');
        const v = el.value.trim();
        if (!v) bad.push([el, `${labelFor(el)} is missing.`]);
        else if (el.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) bad.push([el, 'That email address doesn’t look right.']);
      });
      if (summary) {
        const list = summary.querySelector('ul');
        list.innerHTML = '';
        bad.forEach(([el, msg]) => {
          el.setAttribute('aria-invalid', 'true');
          const li = document.createElement('li'); const a = document.createElement('a'); a.href = `#${el.id}`; a.textContent = msg;
          a.addEventListener('click', (e) => { e.preventDefault(); el.focus(); el.scrollIntoView({ block: 'center', behavior: reduce.matches ? 'auto' : 'smooth' }); });
          li.appendChild(a); list.appendChild(li);
        });
        summary.hidden = bad.length === 0;
        if (bad.length) { summary.querySelector('[data-error-title]').textContent = bad.length === 1 ? 'One thing to fill in first:' : 'A couple of things to fill in first:'; summary.focus(); }
      }
      return bad.length === 0;
    };
    intake.addEventListener('submit', (e) => {
      if (!check()) { e.preventDefault(); return; }
      if (intake.querySelector('[name="sw_trap_field"]').value) { e.preventDefault(); return; }
      if (key) { if (status) status.textContent = 'Sending…'; return; }
      // No access key yet: open a pre-filled email with every answer, so nothing is lost.
      e.preventDefault();
      const lines = [];
      intake.querySelectorAll('input, textarea').forEach((el) => {
        if (el.type === 'hidden' || el.type === 'checkbox' && !el.checked || el.type === 'radio' && !el.checked || el.name === 'sw_trap_field' || el.name === 'botcheck') return;
        if (!el.value.trim()) return;
        const lab = el.type === 'checkbox' || el.type === 'radio' ? (el.closest('fieldset')?.querySelector('legend')?.textContent.replace(/\s*\(pick any\)\s*/i, '').trim() || el.name) : labelFor(el);
        lines.push(`${lab}: ${el.value.trim()}`);
      });
      const subject = encodeURIComponent(`New project: ${business ? business.value.trim() : ''}`.trim());
      const body = encodeURIComponent(lines.join('\n\n'));
      location.href = `mailto:${fallback}?subject=${subject}&body=${body}`;
      if (status) status.textContent = 'Your email app should open with your answers filled in. If it didn’t, email them to ' + fallback + '.';
    });
  }
})();
