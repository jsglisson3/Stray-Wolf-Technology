/* Stray Wolf Technology. Small, plain script: the menu, the reveals, the hero sites, the service tabs, the work carousel, the fit check and the intake form.
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
  document.querySelectorAll('.ruler-steps, .faqs, .shows, .pledges, .pv-cards').forEach((group) => {
    group.querySelectorAll(':scope > [data-reveal], :scope > * > [data-reveal]').forEach((el, i) => el.style.setProperty('--rd', `${Math.min(i, 6) * 80}ms`));
  });

  /* ---- The hero: one real site at a time on its stone panel. It changes by itself; the caption and link follow,
     and a thin orange line along the rule shows when the next one is coming.
     Hovering with a mouse, focusing or pressing Next stops it. Nothing moves when the visitor asked for reduced motion. */
  document.querySelectorAll('[data-sites]').forEach((box) => {
    const imgs = [...box.querySelectorAll('[data-site-img]')];
    if (imgs.length < 2) return;
    const name = box.querySelector('[data-site-name]');
    const link = box.querySelector('[data-site-link]');
    const domain = box.querySelector('[data-site-domain]');
    const now = box.querySelector('[data-site-now]');
    const frame = box.querySelector('[data-site-frame]');
    const next = box.querySelector('[data-site-next]');
    const every = +box.dataset.every || 5200;
    box.style.setProperty('--tick', every + 'ms');
    let i = 0, timer = null, stopped = reduce.matches, seen = false;
    const tick = (on) => { box.classList.remove('is-ticking'); if (on) { void box.offsetWidth; box.classList.add('is-ticking'); } };
    const show = (n) => {
      i = (n + imgs.length) % imgs.length;
      imgs.forEach((im, k) => im.classList.toggle('is-on', k === i));
      const d = imgs[i].dataset;
      if (name) name.textContent = d.name;
      if (link) link.href = d.link;
      if (domain) domain.textContent = d.domain;
      if (now) now.textContent = String(i + 1);
      if (frame) frame.href = d.link;
    };
    const stop = () => { clearInterval(timer); timer = null; tick(false); };
    const start = () => {
      if (stopped || timer || !seen || document.hidden) return;
      tick(true);
      timer = setInterval(() => { show(i + 1); tick(true); }, every);
    };
    if (next) next.addEventListener('click', () => { show(i + 1); stopped = true; stop(); });
    box.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') stop(); });
    box.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse' && !box.matches(':focus-within')) start(); });
    box.addEventListener('focusin', stop);
    box.addEventListener('focusout', () => setTimeout(() => { if (!box.matches(':focus-within')) start(); }, 0));
    document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));
    if ('IntersectionObserver' in window) {
      new IntersectionObserver((es) => es.forEach((en) => { seen = en.isIntersecting; en.isIntersecting ? start() : stop(); }), { threshold: 0.3 }).observe(box);
    } else { seen = true; start(); }
  });

  /* ---- How it works: an orange line runs along the 30-day ruler as you scroll past it,
     and each step lights up once the line reaches its day ---- */
  document.querySelectorAll('[data-timeline]').forEach((tl) => {
    const steps = Array.from(tl.querySelectorAll('[data-day]'));
    const at = steps.map((s) => Math.max(0, (parseInt(s.dataset.day, 10) - 1) / 29));
    const set = (p) => {
      tl.style.setProperty('--p', p.toFixed(3));
      steps.forEach((s, i) => s.classList.toggle('is-reached', p >= at[i] - 0.001 && p > 0));
    };
    if (reduce.matches) { set(1); return; }
    let ticking = false;
    const update = () => {
      ticking = false;
      const r = tl.getBoundingClientRect();
      const from = innerHeight * 0.8;            // the line starts when the ruler is this far down the screen
      const span = Math.max(1, r.height + innerHeight * 0.25);
      set(Math.min(1, Math.max(0, (from - r.top) / span)));
    };
    addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    addEventListener('resize', update);
    update();
  });

  /* ---- What I do: four tabs, each playing a short scene of the service at work ----------
     A thin bar under the chosen tab fills while its scene plays, then the next tab takes over.
     It rests while a pointer or keyboard is inside, or it's off screen; choosing a tab stops it for good. */
  document.querySelectorAll('[data-svc]').forEach((svc) => {
    const tabs = Array.from(svc.querySelectorAll('[role="tab"]'));
    const panels = tabs.map((t) => document.getElementById(t.getAttribute('aria-controls')));
    if (!tabs.length || panels.some((p) => !p)) return;
    let at = Math.max(0, tabs.findIndex((t) => t.getAttribute('aria-selected') === 'true'));
    const select = (i, focus) => {
      at = (i + tabs.length) % tabs.length;
      tabs.forEach((t, j) => {
        const on = j === at;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        panels[j].classList.toggle('is-active', on);
      });
      if (focus) tabs[at].focus();
    };
    const stop = () => svc.classList.remove('is-auto', 'is-paused');
    tabs.forEach((t, i) => t.addEventListener('click', () => { stop(); select(i); }));
    svc.querySelector('[role="tablist"]').addEventListener('keydown', (e) => {
      const go = { ArrowDown: at + 1, ArrowRight: at + 1, ArrowUp: at - 1, ArrowLeft: at - 1, Home: 0, End: tabs.length - 1 }[e.key];
      if (go === undefined) return;
      e.preventDefault();
      stop();
      select(go, true);
    });

    if (reduce.matches || !('IntersectionObserver' in window)) return;
    let onScreen = false; let hovered = false; let focused = false; let started = false;
    const check = () => {
      if (onScreen && !started) { started = true; svc.classList.add('is-auto'); }
      svc.classList.toggle('is-paused', svc.classList.contains('is-auto') && (!onScreen || hovered || focused || document.hidden));
    };
    // the bar under the chosen tab has filled: on to the next one
    svc.addEventListener('animationend', (e) => {
      if (e.animationName !== 'svc-timer' || !svc.classList.contains('is-auto')) return;
      select(at + 1);
    });
    svc.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') { hovered = true; check(); } });
    svc.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse') { hovered = false; check(); } });
    svc.addEventListener('focusin', () => { focused = true; check(); });
    svc.addEventListener('focusout', (e) => { if (!svc.contains(e.relatedTarget)) { focused = false; check(); } });
    document.addEventListener('visibilitychange', check);
    new IntersectionObserver((entries) => { onScreen = entries[entries.length - 1].isIntersecting; check(); }, { threshold: 0.35 }).observe(svc);
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
        if (mini) mini.textContent = best.querySelector('legend').textContent.replace(/^[\d\s/]+/, '').trim();
      }, { threshold: [0, 0.25, 0.5, 0.75, 1], rootMargin: '-20% 0px -40% 0px' });
      groups.forEach((g) => io.observe(g));
    }
  }

  /* ---- About: is this a fit? Three yes/no questions, answered on the page, sent nowhere ---- */
  document.querySelectorAll('[data-fitcheck]').forEach((box) => {
    const result = box.querySelector('[data-fit-result]');
    if (!result) return;
    const answers = {};
    const say = (cls, h, p, cta) => {
      result.className = 'fit-result' + (cls ? ' ' + cls : '');
      result.innerHTML = `<p class="fit-result-h">${h}</p><p class="fit-result-p">${p}</p>` +
        (cta ? '<a class="button" href="start.html">Start a project<svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></a>' : '');
    };
    const update = () => {
      const { own, one, ref } = answers;
      if (own === undefined || one === undefined || ref === undefined) {
        const n = Object.keys(answers).length;
        say('', n ? `${3 - n} more to go.` : 'Answer the three questions and I’ll tell you honestly.', 'If it’s not a fit, I’ll say so up front.', false);
      } else if (own === 'no') {
        say('is-no', 'Probably not the right fit.', 'A franchise with a head office, a large online store or a project that needs a full team is better served by an agency. If you’re not sure, ask anyway and I’ll point you the right way.', false);
      } else if (one === 'no') {
        say('is-no', 'Honest answer: maybe not.', 'If you’d rather have a team and an account manager, an agency will suit you better. If you want one person who does the work and answers the phone, that’s me.', false);
      } else if (ref === 'no') {
        say('is-maybe', 'Could well be a fit.', 'I work mostly by referral, but tell me about your business and I’ll give you a straight answer within five days.', true);
      } else {
        say('is-yes', 'Sounds like a fit.', 'Fourteen questions, about five minutes, and you’ll hear from me within five days with a price in writing.', true);
      }
    };
    box.querySelectorAll('[data-fq]').forEach((row) => {
      const buttons = row.querySelectorAll('[data-ans]');
      buttons.forEach((b) => b.addEventListener('click', () => {
        answers[row.dataset.fq] = b.dataset.ans;
        buttons.forEach((o) => o.setAttribute('aria-pressed', String(o === b)));
        update();
      }));
    });
  });

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
