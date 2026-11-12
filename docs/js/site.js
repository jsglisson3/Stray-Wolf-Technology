/* Stray Wolf Technology. Small, plain script: the menu, the reveals, the hero sites, the work carousel and the intake form.
   Everything on the page works without it; this only adds the moving parts. */
(() => {
  'use strict';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');

  /* ---- The header: frosted once the page moves, tucked away while reading down, back on any scroll up ---- */
  const header = document.querySelector('[data-header]');
  const menuIsOpen = () => document.documentElement.classList.contains('menu-open');
  if (header) {
    // Fixed numbers with some slack, so nothing flips back and forth near a threshold: the rule darkens once the
    // page has moved; the bar tucks away after a clear scroll down past the top, and comes back after a clear
    // scroll up, or near the top. The bar never changes height, so the page under it never jumps.
    const SLACK = 28, TOP = 180;
    let lastY = Math.max(0, scrollY), turnY = lastY, dir = 0, hidden = false, ticking = false;
    const onScroll = () => {
      const y = Math.max(0, scrollY);
      if (y > 24) header.classList.add('is-scrolled'); else if (y < 4) header.classList.remove('is-scrolled');
      if (!menuIsOpen()) {
        const d = y > lastY ? 1 : y < lastY ? -1 : 0;
        if (d && d !== dir) { dir = d; turnY = lastY; }
        const moved = y - turnY;
        if (!hidden && moved > SLACK && y > TOP) { hidden = true; header.classList.add('is-hidden'); }
        else if (hidden && (moved < -SLACK || y < TOP / 2)) { hidden = false; header.classList.remove('is-hidden'); }
      }
      lastY = y; ticking = false;
    };
    addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
    onScroll();
    // following a link to a spot further down the same page shouldn't flash the header away and back
    header.addEventListener('focusin', () => { hidden = false; header.classList.remove('is-hidden'); });
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
    matchMedia('(min-width: 64em)').addEventListener('change', (m) => { if (m.matches) setOpen(false); });   // where the full menu takes over (site.css)
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

  /* ---- The Start form: a question's number turns from sage to ink once it has an answer ---- */
  document.querySelectorAll('#qs-project .q').forEach((q) => {
    const mark = () => q.classList.toggle('is-filled', [...q.querySelectorAll('input, textarea')].some((f) => f.type === 'checkbox' || f.type === 'radio' ? f.checked : f.value.trim() !== ''));
    q.addEventListener('input', mark); q.addEventListener('change', mark); mark();
  });

  /* ---- The stone facets drift a little with the scroll, so the big bands have some depth ---- */
  const facetBands = [...document.querySelectorAll('.has-facets')];
  if (facetBands.length && !reduce.matches) {
    let ticking = false;
    const drift = () => {
      ticking = false;
      const vh = innerHeight;
      for (const el of facetBands) {
        const r = el.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) continue;
        el.style.setProperty('--py', `${((r.top + r.height / 2 - vh / 2) * 0.08).toFixed(1)}px`);
      }
    };
    addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(drift); } }, { passive: true });
    drift();
  }


  /* ---- Groups reveal one after another (a short stagger) ---------------------------- */
  document.querySelectorAll('.phases, .faqs, .shows, .pledges, .pv-cards, .svc-list, .rates').forEach((group) => {
    group.querySelectorAll(':scope > [data-reveal], :scope > * > [data-reveal]').forEach((el, i) => el.style.setProperty('--rd', `${Math.min(i, 6) * 80}ms`));
  });

  /* ---- The work carousel: big centred slides that move on by themselves ---------------------
     The bar in the current dot fills over a few seconds, then the next site slides in (and round again).
     It rests while a pointer or keyboard is inside it, while it's off screen or the tab is hidden.
     The pause button, or a swipe, stops it until someone presses play. No moving at all for reduced motion. */
  document.querySelectorAll('[data-carousel]').forEach((car) => {
    const track = car.querySelector('[data-track]');
    const prev = car.querySelector('[data-prev]');
    const next = car.querySelector('[data-next]');
    if (!track || !prev || !next) return;
    const play = car.querySelector('[data-play]');
    const slides = Array.from(track.children);
    const dots = Array.from(car.querySelectorAll('[data-dot]'));
    const now = car.querySelector('[data-count-now]');
    slides.forEach((s, i) => { s.setAttribute('aria-roledescription', 'slide'); s.setAttribute('aria-label', `${i + 1} of ${slides.length}`); });
    track.setAttribute('aria-roledescription', 'carousel');
    // the slide whose middle is nearest the middle of the row
    const current = () => {
      const r = track.getBoundingClientRect();
      const mid = r.left + r.width / 2;
      let best = 0; let dist = Infinity;
      slides.forEach((s, i) => { const b = s.getBoundingClientRect(); const d = Math.abs(b.left + b.width / 2 - mid); if (d < dist) { dist = d; best = i; } });
      return best;
    };
    let shown = -1;
    const update = () => {
      const i = current();
      if (i === shown) return;
      shown = i;
      slides.forEach((s, j) => s.classList.toggle('is-active', j === i));
      dots.forEach((d, j) => d.setAttribute('aria-current', String(j === i)));
      if (now) now.textContent = String(i + 1).padStart(2, '0');
    };
    const goTo = (i) => {
      const n = slides.length;
      const s = slides[((i % n) + n) % n];
      const r = track.getBoundingClientRect();
      const b = s.getBoundingClientRect();
      track.scrollTo({ left: track.scrollLeft + (b.left + b.width / 2) - (r.left + r.width / 2), behavior: reduce.matches ? 'auto' : 'smooth' });
    };
    prev.addEventListener('click', () => goTo(current() - 1));
    next.addEventListener('click', () => goTo(current() + 1));
    dots.forEach((d, i) => d.addEventListener('click', () => goTo(i)));
    let raf = 0;
    track.addEventListener('scroll', () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(update); }, { passive: true });
    track.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); goTo(current() + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); goTo(current() - 1); }
    });
    addEventListener('resize', () => { shown = -1; update(); });
    update();

    const delay = parseInt(car.dataset.autoplay, 10);
    if (!delay || reduce.matches || !('IntersectionObserver' in window)) { car.classList.add('no-autoplay'); return; }
    car.style.setProperty('--auto', `${delay}ms`);
    let stopped = false; let onScreen = false; let hovered = false; let focused = false;
    const check = () => {
      car.classList.toggle('is-auto', !stopped);
      car.classList.toggle('is-stopped', stopped);
      car.classList.toggle('is-paused', !stopped && (!onScreen || hovered || focused || document.hidden));
      if (play) play.setAttribute('aria-label', stopped ? 'Play the slideshow' : 'Pause the slideshow');
    };
    // the bar in the current dot has filled: on to the next site
    car.addEventListener('animationend', (e) => {
      if (e.animationName !== 'dot-fill' || stopped) return;
      goTo(current() + 1);
    });
    if (play) play.addEventListener('click', () => { stopped = !stopped; check(); });
    // a swipe means someone is looking for themselves
    track.addEventListener('pointerdown', (e) => { if (e.pointerType !== 'mouse' && !stopped) { stopped = true; check(); } });
    car.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') { hovered = true; check(); } });
    car.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse') { hovered = false; check(); } });
    car.addEventListener('focusin', () => { focused = true; check(); });
    car.addEventListener('focusout', (e) => { if (!car.contains(e.relatedTarget)) { focused = false; check(); } });
    document.addEventListener('visibilitychange', check);
    new IntersectionObserver((entries) => { onScreen = entries[entries.length - 1].isIntersecting; check(); }, { threshold: 0.35 }).observe(car);
    check();
  });

  /* ---- The footer scene: a pause button, and no animating while it is off screen ---------- */
  document.querySelectorAll('[data-scene]').forEach((scene) => {
    const btn = scene.querySelector('[data-scene-toggle]');
    if (btn) btn.addEventListener('click', () => {
      const paused = scene.classList.toggle('is-paused');
      document.documentElement.classList.toggle('scene-paused', paused);   // the header sky and the hero wolf stop with it
      btn.setAttribute('aria-label', paused ? 'Play the animation' : 'Pause the animation');
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver((es) => es.forEach((en) => scene.classList.toggle('is-off', !en.isIntersecting))).observe(scene);
    }
  });

  /* ---- Questions: only one answer open at a time ------------------------------------ */
  const faqs = document.querySelectorAll('.faq');
  faqs.forEach((d) => d.addEventListener('toggle', () => { if (d.open) faqs.forEach((o) => { if (o !== d) o.open = false; }); }));

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
      return l ? l.textContent.replace(/^\s*0?\d\s*/, '').replace(/\s*\((required|optional)\)\s*/i, '').trim() : el.name;
    };
    const check = () => {
      const bad = [];
      intake.querySelectorAll('[required]').forEach((el) => {
        el.removeAttribute('aria-invalid');
        const v = el.type === 'checkbox' ? (el.checked ? 'yes' : '') : el.value.trim();
        if (!v) bad.push([el, el.dataset.msg || `${labelFor(el)} is missing.`]);
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
        const lab = el.type === 'checkbox' || el.type === 'radio' ? (el.closest('fieldset')?.querySelector('legend')?.textContent.replace(/^\s*0?\d\s*/, '').replace(/\s*\(pick any\)\s*/i, '').trim() || el.name) : labelFor(el);
        lines.push(`${lab}: ${el.value.trim()}`);
      });
      const subject = encodeURIComponent(`New project: ${business ? business.value.trim() : ''}`.trim());
      const body = encodeURIComponent(lines.join('\n\n'));
      location.href = `mailto:${fallback}?subject=${subject}&body=${body}`;
      if (status) status.textContent = 'Your email app should open with your answers filled in. If it didn’t, email them to ' + fallback + '.';
    });
  }
})();

/* Moon door (Nov 12 2026, Jeremy: "if i hold the moon it starts to slowly go bright and phase into an admin page").
   Hold the footer moon for 2 seconds: a soft moonlight grows from it, then washes over the whole page, and
   /admin/ comes up out of the light (the admin page fades in from the same colour). Let go early and the light
   fades away. Nothing shows or links to it; a normal tap does nothing. Same effect as the client sites' doors. */
(() => {
  const WASH = '#FFFDF8', HOLD = 2000, TO = '/admin/';
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let timer = 0, glow = null, glowAnim = null, opened = false, sx = 0, sy = 0;
  const layer = (css) => { const d = document.createElement('div'); d.setAttribute('aria-hidden', 'true'); d.setAttribute('data-moon-light', ''); d.style.cssText = 'position:fixed;pointer-events:none;z-index:2147483646;' + css; document.body.appendChild(d); return d; };
  document.querySelectorAll('[data-moon-door]').forEach((el) => { el.style.touchAction = 'none'; el.style.webkitTouchCallout = 'none'; el.style.userSelect = 'none'; el.style.webkitUserSelect = 'none'; });
  const reset = () => {
    clearTimeout(timer); timer = 0;
    if (!glow) return;
    const g = glow; glow = null;
    const cs = getComputedStyle(g), o = cs.opacity, t = cs.transform;
    if (glowAnim) glowAnim.cancel();
    g.animate([{ opacity: o, transform: t }, { opacity: 0, transform: t }], { duration: 380, easing: 'ease-out', fill: 'forwards' }).onfinish = () => g.remove();
  };
  const start = (e, el) => {
    if (e.button > 0) return;
    reset(); opened = false; sx = e.clientX; sy = e.clientY;
    const r = (el.querySelector('[data-door-center]') || el).getBoundingClientRect();
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2, size = Math.max(110, Math.max(r.width, r.height) * 3.4);
    glow = layer(`left:${cx - size / 2}px;top:${cy - size / 2}px;width:${size}px;height:${size}px;border-radius:50%;opacity:0;mix-blend-mode:screen;` +
      `background:radial-gradient(circle,${WASH} 0,${WASH} 9%,rgba(255,250,236,.85) 18%,rgba(255,240,214,.4) 38%,rgba(255,236,206,.12) 54%,rgba(255,236,206,0) 70%)`);
    glowAnim = glow.animate([{ opacity: 0, transform: 'scale(.35)' }, { opacity: 0.7, transform: 'scale(.8)', offset: 0.45 }, { opacity: 1, transform: 'scale(1.3)' }], { duration: HOLD, easing: 'cubic-bezier(.4,0,.7,1)', fill: 'forwards' });
    timer = setTimeout(() => {
      opened = true; timer = 0;
      try { sessionStorage.setItem('sw-moonlight', '1'); } catch (x) { /* private mode: no fade-in, still opens */ }
      if (navigator.vibrate) try { navigator.vibrate(12); } catch (x) { /* not on this device */ }
      const far = Math.max(Math.hypot(cx, cy), Math.hypot(innerWidth - cx, cy), Math.hypot(cx, innerHeight - cy), Math.hypot(innerWidth - cx, innerHeight - cy));
      const d = far * 4 + 200, from = Math.min(1, size * 0.9 / d);
      const wash = layer(`left:${cx - d / 2}px;top:${cy - d / 2}px;width:${d}px;height:${d}px;border-radius:50%;transform:scale(${from});` +
        `background:radial-gradient(circle,${WASH} 0,${WASH} 50%,rgba(255,253,248,.85) 66%,rgba(255,250,236,.35) 84%,rgba(255,250,236,0) 100%)`);
      const go = () => { location.href = TO; };
      if (calm) { wash.style.transform = 'none'; setTimeout(go, 120); return; }
      wash.animate([{ transform: `scale(${from})` }, { transform: 'scale(1)' }], { duration: 800, easing: 'cubic-bezier(.6,0,.8,.5)', fill: 'forwards' }).onfinish = go;
      setTimeout(go, 1200);
    }, HOLD);
  };
  document.addEventListener('pointerdown', (e) => { const el = e.target.closest && e.target.closest('[data-moon-door]'); if (el) start(e, el); }, true);
  document.addEventListener('pointermove', (e) => { if (timer && Math.abs(e.clientX - sx) + Math.abs(e.clientY - sy) > 14) reset(); }, true);
  ['pointerup', 'pointercancel'].forEach((n) => addEventListener(n, () => { if (timer && !opened) reset(); }, true));
  document.addEventListener('contextmenu', (e) => { if (e.target.closest && e.target.closest('[data-moon-door]') && (timer || opened)) e.preventDefault(); }, true);
  addEventListener('pageshow', (e) => { if (e.persisted) { opened = false; document.querySelectorAll('[data-moon-light]').forEach((d) => d.remove()); } });
})();
