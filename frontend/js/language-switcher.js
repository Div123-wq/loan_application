(function(){
  const LANG_KEY = 'll_lang';
  const SUPPORTED_LANGS = new Set(['en', 'hi', 'kn', 'ta', 'te', 'ml', 'mr']);

  function normalizeLang(lang) {
    return SUPPORTED_LANGS.has(lang) ? lang : 'en';
  }

  function syncSelects(lang) {
    document.querySelectorAll('.language-select').forEach(select => {
      select.value = lang;
    });
  }

  function syncPageSpecificLanguage(lang) {
    const chatLanguageSelect = document.getElementById('langSelect');
    if (
      chatLanguageSelect &&
      !chatLanguageSelect.classList.contains('language-select') &&
      typeof window.changeLanguage === 'function'
    ) {
      chatLanguageSelect.value = lang;
      window.changeLanguage(true);
    }
  }

  function setGoogleTranslateCookie(lang) {
    const value = lang === 'en' ? '/en/en' : `/en/${lang}`;
    const expires = 'expires=Fri, 31 Dec 9999 23:59:59 GMT';
    document.cookie = `googtrans=${value}; ${expires}; path=/`;

    const hostname = window.location.hostname;
    if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1') {
      document.cookie = `googtrans=${value}; ${expires}; path=/; domain=.${hostname}`;
    }
  }

  function observeGoogleCombo() {
    const combo = document.querySelector('.goog-te-combo');
    if (!combo || combo.dataset.finscanBound === '1') return;

    combo.dataset.finscanBound = '1';
    combo.addEventListener('change', () => {
      const lang = normalizeLang(combo.value || 'en');
      try { localStorage.setItem(LANG_KEY, lang); } catch(e) {}
      document.documentElement.lang = lang;
      syncSelects(lang);
      syncPageSpecificLanguage(lang);
    });
  }

  function scheduleGoogleReload(lang) {
    const reloadKey = `ll_translate_reload_${window.location.pathname}`;
    const currentReloadLang = sessionStorage.getItem(reloadKey);

    if (currentReloadLang === lang) return;

    sessionStorage.setItem(reloadKey, lang);
    setTimeout(() => window.location.reload(), 700);
  }

  function dispatchGoogleChange(combo) {
    if (document.createEvent) {
      const event = document.createEvent('HTMLEvents');
      event.initEvent('change', true, true);
      combo.dispatchEvent(event);
      return;
    }

    if (combo.fireEvent) {
      combo.fireEvent('onchange');
    }
  }

  function triggerGoogleTranslate(lang, attempt) {
    const combo = document.querySelector('.goog-te-combo');
    if (combo) {
      observeGoogleCombo();
      combo.value = lang === 'en' ? '' : lang;
      dispatchGoogleChange(combo);
      return;
    }

    if (attempt < 40) {
      setTimeout(() => triggerGoogleTranslate(lang, attempt + 1), 250);
      return;
    }

    scheduleGoogleReload(lang);
  }

  function changeSiteLanguage(lang) {
    const targetLang = normalizeLang(lang);
    try { localStorage.setItem(LANG_KEY, targetLang); } catch(e) {}
    document.documentElement.lang = targetLang;
    syncSelects(targetLang);
    syncPageSpecificLanguage(targetLang);
    setGoogleTranslateCookie(targetLang);

    fetch(`/api/set_language?lang=${targetLang}`).catch(() => {});

    if (window.appI18n) {
      try { window.appI18n.setLang(targetLang); } catch(e) { console.warn(e); }
    }

    triggerGoogleTranslate(targetLang, 0);

    if (!window.appI18n) {
      scheduleGoogleReload(targetLang);
    }
  }

  function initLanguageSwitcher() {
    const savedLang = normalizeLang(localStorage.getItem(LANG_KEY) || 'en');
    document.documentElement.lang = savedLang;
    syncSelects(savedLang);
    syncPageSpecificLanguage(savedLang);

    document.querySelectorAll('.language-select').forEach(select => {
      select.addEventListener('change', event => changeSiteLanguage(event.target.value));
    });

    observeGoogleCombo();
    setInterval(observeGoogleCombo, 500);

    if (savedLang !== 'en') {
      setGoogleTranslateCookie(savedLang);
      triggerGoogleTranslate(savedLang, 0);
      if (!window.appI18n) {
        scheduleGoogleReload(savedLang);
      }
    }
  }

  window.changeSiteLanguage = changeSiteLanguage;
  window.changeLang = window.changeLang || changeSiteLanguage;
  window.onGoogleTranslateReady = function() {
    const savedLang = normalizeLang(localStorage.getItem(LANG_KEY) || 'en');
    observeGoogleCombo();
    triggerGoogleTranslate(savedLang, 0);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLanguageSwitcher);
  } else {
    initLanguageSwitcher();
  }
})();
