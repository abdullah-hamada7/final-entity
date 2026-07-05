/* Entity Medical - Profile page helpers */
(function () {
  'use strict';

  function initProfileStats() {
    const statFavs = document.getElementById('statFavs');
    if (!statFavs) return;

    try {
      const favs = JSON.parse(localStorage.getItem('userFavorites') || '[]');
      statFavs.textContent = Array.isArray(favs) ? String(favs.length) : '0';
    } catch (_e) {
      statFavs.textContent = '0';
    }
  }

  document.addEventListener('DOMContentLoaded', initProfileStats);
})();
