
    if(!localStorage.getItem('ll_user') && !window.location.search.includes('demo=1')) {
      window.location.href = 'auth.html';
    }
  