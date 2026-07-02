// Simple frontend i18n loader using JSON files in /i18n/
/* Frontend i18n loader
   - Initializes after DOMContentLoaded
   - Replaces elements with data-i18n using innerHTML (preserve markup)
*/
(function(){
  const LANG_KEY = 'll_lang';

  async function loadTranslations(lang){
    try{
      const url = (window.location.origin && window.location.origin !== 'null') ? `${window.location.origin}/i18n/${lang}.json` : `/i18n/${lang}.json`;
      const res = await fetch(url + '?_=' + Date.now());
      console.log('i18n: loading', url);
      if(!res.ok) throw new Error('missing translations: ' + res.status);
      const dict = await res.json();
      if(dict.title) document.title = dict.title;
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if(dict[key] !== undefined) el.innerHTML = dict[key];
      });
    }catch(e){
      console.warn('i18n load failed for', lang, e);
    }
  }

  function setLang(lang){
    try { localStorage.setItem(LANG_KEY, lang); } catch(e){}
    fetch(`/api/set_language?lang=${lang}`).catch(()=>{});
    loadTranslations(lang);
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
