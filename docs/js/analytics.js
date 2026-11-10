/* Stray Wolf Technology: Google Analytics 4 (Jeremy, Nov 10 2026: GA4 on, no consent banner).
   Loaded only when GA4_ID is set in tools/build.py; the ID comes from this tag's data-ga attribute.
   Kept in its own file so the Content-Security-Policy never has to allow inline scripts.

   Events sent (besides GA4's own page_view and enhanced measurement):
   - generate_lead : the thanks page, which people only reach after the form is sent. Sent once per browser session,
                     so a refresh or the back button never counts the same lead twice. Mark this one as a Key event in GA4.
   - email_click   : a mailto: link
   - phone_click   : a tel: link (only shows once PHONE is set)
   - cta_click     : any "Start a project" link, with where on the page it was (header, hero, close, footer...) */
(() => {
  'use strict';
  const tag = document.currentScript;
  const id = tag && tag.dataset.ga;
  if (!id || !/^G-[A-Z0-9]+$/.test(id)) return;

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;
  gtag('js', new Date());
  gtag('config', id);

  const s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
  document.head.appendChild(s);

  // a form lead: counted on arrival at the thanks page, once per session
  if (/\/thanks(\.html)?$/.test(location.pathname)) {
    let seen = false;
    try { seen = sessionStorage.getItem('sw-lead') === '1'; sessionStorage.setItem('sw-lead', '1'); } catch (e) { /* storage blocked: count it */ }
    if (!seen) gtag('event', 'generate_lead', { form_name: 'start_project' });
  }

  // where on the page a link sits, in plain words
  const where = (a) => {
    if (a.closest('.site-header')) return 'header';
    if (a.closest('.site-footer')) return 'footer';
    if (a.closest('.hero')) return 'hero';
    if (a.closest('.close-wrap')) return 'close';
    const sec = a.closest('section[id], section[aria-labelledby]');
    return sec ? (sec.id || sec.getAttribute('aria-labelledby')) : 'page';
  };
  document.addEventListener('click', (e) => {
    const a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    const href = a.getAttribute('href');
    if (href.startsWith('mailto:')) gtag('event', 'email_click', { link_location: where(a) });
    else if (href.startsWith('tel:')) gtag('event', 'phone_click', { link_location: where(a) });
    else if (/(^|\/)start\.html(\?|#|$)/.test(href)) gtag('event', 'cta_click', { link_text: a.textContent.trim().slice(0, 60), link_location: where(a) });
  }, { capture: true });
})();
