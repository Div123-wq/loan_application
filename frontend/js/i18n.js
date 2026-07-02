// Simple frontend i18n loader using JSON files in /i18n/
/* Frontend i18n loader
   - Initializes after DOMContentLoaded
   - Replaces elements with data-i18n using innerHTML (preserve markup)
*/
(function(){
  const LANG_KEY = 'll_lang';
  const SUPPORTED_LANGS = new Set(['en', 'hi', 'kn', 'ta', 'te', 'ml', 'mr']);

  async function loadTranslations(lang){
    const targetLang = SUPPORTED_LANGS.has(lang) ? lang : 'en';
    try{
      const url = `i18n/${targetLang}.json`;
      const res = await fetch(url + '?_=' + Date.now());
      console.log('i18n: loading', url);
      if(!res.ok) throw new Error('missing translations: ' + res.status);
      const dict = await res.json();
      if(dict.title) document.title = dict.title;
      document.documentElement.lang = targetLang;
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if(dict[key] !== undefined) el.innerHTML = dict[key];
      });
    }catch(e){
      console.warn('i18n load failed for', targetLang, e);
    }
  }

  function setLang(lang){
    const targetLang = SUPPORTED_LANGS.has(lang) ? lang : 'en';
    try { localStorage.setItem(LANG_KEY, targetLang); } catch(e){}
    fetch(`/api/set_language?lang=${targetLang}`).catch(()=>{});
    loadTranslations(targetLang);
  }

  function init(){
    const defaultLang = localStorage.getItem(LANG_KEY) || 'en';
    const sel = document.getElementById('langSelect');
    if(sel){
      sel.value = defaultLang;
      sel.addEventListener('change', (e)=> setLang(e.target.value));
    }
    loadTranslations(defaultLang);
    window.appI18n = { setLang, loadTranslations };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
