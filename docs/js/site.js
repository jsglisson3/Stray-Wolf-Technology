/* Stray Wolf Technology. Small, plain script: the menu, the reveals, the work carousel and the intake form.
   Everything on the page works without it; this only adds the moving parts. */
(() => {
  'use strict';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');

  /* ---- The header: frosted once the page moves, tucked away while reading down, back on any scroll up ---- */
  const header = document.querySelector('[data-header]');
  const menuIsOpen = () => document.documentElement.classList.contains('menu-open');
  if (header) {
    let lastY = scrollY;
    let ticking = false;
    const onScroll = () => {
      const y = Math.max(0, scrollY);
      const start = header.offsetHeight * 2;
      header.classList.toggle('is-scrolled', y > 8);
      if (!menuIsOpen()) {
        if (y > lastY + 6 && y > start) header.classList.add('is-hidden');
        else if (y < lastY - 6 || y <= start) header.classList.remove('is-hidden');
      }
      if (Math.abs(y - lastY) > 6) lastY = y;
      ticking = false;
    };
    addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
    onScroll();
    // following a link to a spot further down the same page shouldn't flash the header away and back
    header.addEventListener('focusin', () => header.classList.remove('is-hidden'));
  }

  /* ---- The phone menu: a full sheet under the header ---------------------------------- */
  const toggle = document.querySelector('[data-menu-toggle]');
  const nav = document.getElementById('site-nav');
  if (toggle && nav) {
    const label = toggle.querySelector('[data-menu-label]');
    const root = document.documentElement;
    const setOpen = (open) => {
      if (open && header) {
        header.classList.remove('is-hidden');
        root.style.setProperty('--menu-top', `${Math.max(0, header.getBoundingClientRect().bottom)}px`);
      }
      toggle.setAttribute('aria-expanded', String(open));
      root.classList.toggle('menu-open', open);
      if (label) label.textContent = open ? 'Close' : 'Menu';
    };
    toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && menuIsOpen()) { setOpen(false); toggle.focus(); } });
    nav.addEventListener('click', (e) => { if (e.target.closest('a')) setOpen(false); });
    // keep keyboard focus inside the open sheet (the toggle, then the links)
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Tab' || !menuIsOpen()) return;
      const items = [toggle, ...nav.querySelectorAll('a')];
      const i = items.indexOf(document.activeElement);
      if (e.shiftKey && i <= 0) { e.preventDefault(); items[items.length - 1].focus(); }
      else if (!e.shiftKey && i === items.length - 1) { e.preventDefault(); items[0].focus(); }
    });
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

  /* ---- Groups reveal one after another (a short stagger) ---------------------------- */
  document.querySelectorAll('.bento, .timeline, .numbers, .faqs, .shows, .principles, .fit, .pv-cards').forEach((group) => {
    group.querySelectorAll(':scope > [data-reveal], :scope > * > [data-reveal]').forEach((el, i) => el.style.setProperty('--rd', `${Math.min(i, 6) * 80}ms`));
  });

  /* ---- The hero demo: a website going from sketch to finished ------------------------ */
  document.querySelectorAll('[data-demo]').forEach((demo) => {
    const buttons = demo.querySelectorAll('[data-demo-set]');
    let touched = false;
    const set = (state) => {
      demo.dataset.state = state;
      buttons.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.demoSet === state)));
    };
    buttons.forEach((b) => b.addEventListener('click', () => { touched = true; set(b.dataset.demoSet); }));
    if (reduce.matches || !('IntersectionObserver' in window)) { set('built'); return; }
    // plays once by itself when it comes into view: the sketch, then the finished page
    const io = new IntersectionObserver((entries) => {
      if (!entries.some((e) => e.isIntersecting)) return;
      io.disconnect();
      setTimeout(() => { if (!touched) set('built'); }, 1400);
    }, { threshold: 0.4 });
    io.observe(demo);
  });

  /* ---- How it works: the line fills as you scroll past, each step lights up when reached ---- */
  document.querySelectorAll('[data-timeline]').forEach((tl) => {
    const steps = Array.from(tl.querySelectorAll('.tl-step'));
    const nodes = steps.map((s) => s.querySelector('.tl-node'));
    if (reduce.matches) { tl.style.setProperty('--p', '1'); steps.forEach((s) => s.classList.add('is-reached')); return; }
    let ticking = false;
    const update = () => {
      ticking = false;
      const mark = innerHeight * 0.62;   // a step counts as reached once it passes this line on the screen
      const first = nodes[0].getBoundingClientRect();
      const last = nodes[nodes.length - 1].getBoundingClientRect();
      const vertical = Math.abs(last.top - first.top) > Math.abs(last.left - first.left);
      let p;
      if (vertical) p = (mark - first.top) / Math.max(1, last.top - first.top);
      else p = (mark - first.top + 40) / 240;   // side by side: fill across while the row crosses the line
      p = Math.min(1, Math.max(0, p));
      tl.style.setProperty('--p', p.toFixed(3));
      steps.forEach((s, i) => s.classList.toggle('is-reached', p >= (steps.length > 1 ? i / (steps.length - 1) : 1) - 0.001));
    };
    addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    addEventListener('resize', update);
    update();
  });

  /* ---- The work carousel: a scroll-snap row, with buttons, dots and a counter --------- */
  document.querySelectorAll('[data-carousel]').forEach((car) => {
    const track = car.querySelector('[data-track]');
    const prev = car.querySelector('[data-prev]');
    const next = car.querySelector('[data-next]');
    if (!track || !prev || !next) return;
    const slides = Array.from(track.children);
    const dots = Array.from(car.querySelectorAll('[data-dot]'));
    const now = car.querySelector('[data-count-now]');
    slides.forEach((s, i) => { s.setAttribute('aria-roledescription', 'slide'); s.setAttribute('aria-label', `${i + 1} of ${slides.length}`); });
    track.setAttribute('aria-roledescription', 'carousel');
    const current = () => {
      const left = track.getBoundingClientRect().left;
      let best = 0; let dist = Infinity;
      slides.forEach((s, i) => { const d = Math.abs(s.getBoundingClientRect().left - left); if (d < dist) { dist = d; best = i; } });
      const max = track.scrollWidth - track.clientWidth - 2;
      return track.scrollLeft >= max ? slides.length - 1 : best;
    };
    const update = () => {
      const max = track.scrollWidth - track.clientWidth - 2;
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft >= max;
      const i = current();
      slides.forEach((s, j) => s.classList.toggle('is-active', j === i));
      dots.forEach((d, j) => d.setAttribute('aria-current', String(j === i)));
      if (now) now.textContent = String(i + 1).padStart(2, '0');
    };
    const goTo = (i) => {
      const s = slides[Math.max(0, Math.min(slides.length - 1, i))];
      track.scrollTo({ left: s.offsetLeft - track.offsetLeft - parseFloat(getComputedStyle(track).paddingLeft || 0), behavior: reduce.matches ? 'auto' : 'smooth' });
    };
    prev.addEventListener('click', () => goTo(current() - 1));
    next.addEventListener('click', () => goTo(current() + 1));
    dots.forEach((d, i) => d.addEventListener('click', () => goTo(i)));
    let t;
    track.addEventListener('scroll', () => { cancelAnimationFrame(t); t = requestAnimationFrame(update); }, { passive: true });
    track.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight') { e.preventDefault(); goTo(current() + 1); } if (e.key === 'ArrowLeft') { e.preventDefault(); goTo(current() - 1); } });
    window.addEventListener('resize', update);
    update();
  });

  /* ---- Questions: only one answer open at a time ------------------------------------ */
  const faqs = document.querySelectorAll('.faq');
  faqs.forEach((d) => d.addEventListener('toggle', () => { if (d.open) faqs.forEach((o) => { if (o !== d) o.open = false; }); }));

  /* ---- Start a project: count the answers, tick off each section, show where you are ---- */
  const form = document.querySelector('[data-intake]');
  if (form) {
    const groups = Array.from(form.querySelectorAll('[data-qs]'));
    const qs = Array.from(form.querySelectorAll('[data-qs] .q')).filter((q) => !q.closest('.visually-hidden'));
    const answered = (q) => Array.from(q.querySelectorAll('input, textarea')).some((el) => (el.type === 'checkbox' || el.type === 'radio') ? el.checked : el.value.trim() !== '');
    const ready = form.querySelector('[data-form-ready]');
    const readyText = ready ? ready.querySelector('span').textContent : '';
    const mini = document.querySelector('[data-mini-label]');
    const tally = () => {
      const done = qs.filter(answered).length;
      document.querySelectorAll('[data-progress-done]').forEach((el) => { el.textContent = done; });
      document.querySelectorAll('[data-progress-total]').forEach((el) => { el.textContent = qs.length; });
      document.querySelectorAll('[data-progress-bar]').forEach((el) => el.style.setProperty('--done', (done / qs.length).toFixed(3)));
      groups.forEach((g) => {
        const link = document.querySelector(`[data-progress-link="${g.id}"]`);
        if (link) link.classList.toggle('is-started', Array.from(g.querySelectorAll('.q')).some(answered));
      });
      if (ready) {
        const ok = Array.from(form.querySelectorAll('[required]')).every((el) => el.value.trim() !== '' && (el.type !== 'email' || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim())));
        ready.classList.toggle('is-ready', ok);
        ready.querySelector('span').textContent = ok ? 'All the required answers are in. Add anything else you like, then send.' : readyText;
      }
    };
    form.addEventListener('input', tally);
    form.addEventListener('change', tally);
    tally();
    setTimeout(tally, 50);   // after the business name is carried over from the homepage
    if ('IntersectionObserver' in window) {
      const seen = new Map();
      const io = new IntersectionObserver((entries) => {
        entries.forEach((e) => seen.set(e.target, e.isIntersecting ? e.intersectionRatio : 0));
        let best = null; let r = 0;
        seen.forEach((v, k) => { if (v > r) { r = v; best = k; } });
        if (!best) return;
        document.querySelectorAll('[data-progress-link]').forEach((a) => a.classList.toggle('is-current', a.dataset.progressLink === best.id));
        if (mini) mini.textContent = best.querySelector('legend').textContent.replace(/^\d+/, '').trim();
      }, { threshold: [0, 0.25, 0.5, 0.75, 1], rootMargin: '-20% 0px -40% 0px' });
      groups.forEach((g) => io.observe(g));
    }
  }

  /* ---- Privacy: mark the section you're reading in the list ---------------------------- */
  const toc = document.querySelectorAll('.toc a');
  if (toc.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) toc.forEach((a) => a.classList.toggle('is-current', a.getAttribute('href') === `#${e.target.id}`)); });
    }, { rootMargin: '-30% 0px -60% 0px' });
    document.querySelectorAll('.prose section[id]').forEach((s) => io.observe(s));
  }

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
