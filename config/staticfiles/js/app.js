/* Entity Medical - Premium Clean JS
   app.js: global UI + auth + helpers (loaded on all pages)
*/
(function () {
  'use strict';

  const qs = (sel, root = document) => root.querySelector(sel);
  const qsa = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const escapeHtml = (str) =>
    String(str || '').replace(/[&<>"']/g, (m) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[m]));

  const NOTIFY_ICONS = {
    success: 'fa-check-circle',
    error: 'fa-exclamation-circle',
    warning: 'fa-exclamation-triangle',
    info: 'fa-info-circle',
  };

  function showNotify(message, type = 'info', duration = 3200) {
    if (!message) return null;

    const note = document.createElement('div');
    note.className = `app-toast app-toast--${type}`;
    note.setAttribute('role', 'alert');
    note.innerHTML = `<i class="fas ${NOTIFY_ICONS[type] || NOTIFY_ICONS.info}" aria-hidden="true"></i><span>${escapeHtml(message)}</span>`;
    document.body.appendChild(note);

    requestAnimationFrame(() => note.classList.add('show'));
    setTimeout(() => {
      note.classList.remove('show');
      setTimeout(() => note.remove(), 300);
    }, duration);

    return note;
  }

  window.EntityNotify = { show: showNotify };


  function setupSmoothAnchors() {
    qsa('a[href^="#"]').forEach((a) => {
      a.addEventListener('click', (e) => {
        const href = a.getAttribute('href') || '';
        if (href === '#' || href.length < 2) return; // allow default
        const target = qs(href);
        if (!target) return; // allow default if target missing
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  }

  function setupRevealOnScroll() {
    document.documentElement.classList.add('js-reveal');

    if (!('IntersectionObserver' in window)) {
      qsa('.feature-card, .product-card, .service-card, .offer-card, .value-item, .shortcut-card')
        .forEach((el) => el.classList.add('visible'));
      return;
    }

    const els = qsa('.feature-card, .product-card, .service-card, .offer-card, .value-item, .shortcut-card');
    if (!els.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add('visible');
      });
    }, { threshold: 0.1 });

    els.forEach((el) => observer.observe(el));
  }

  function setupContactForm() {
    // Contact form submits to Django backend; validation handled by validation.js
  }



  function setupNavbarScroll() {
    const nav = qs('.navbar');
    if (!nav) return;
    const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  function setupMobileMenu() {
    const hamburger = qs('.hamburger');
    const mobileMenu = qs('.mobile-menu');
    const body = document.body;
    const mobileMenuLinks = qsa('.mobile-menu a');

    if (body) body.classList.remove('menu-open');

    if (hamburger && mobileMenu) {
      const setMenuOpen = (open) => {
        hamburger.classList.toggle('active', open);
        mobileMenu.classList.toggle('active', open);
        body.classList.toggle('menu-open', open);
        hamburger.setAttribute('aria-expanded', open ? 'true' : 'false');
      };

      hamburger.addEventListener('click', () => {
        setMenuOpen(!mobileMenu.classList.contains('active'));
      });

      mobileMenuLinks.forEach(link => {
        link.addEventListener('click', () => setMenuOpen(false));
      });

      mobileMenu.addEventListener('click', (e) => {
        if (e.target === mobileMenu) setMenuOpen(false);
      });
    }

    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        if (hamburger) hamburger.classList.remove('active');
        if (mobileMenu) mobileMenu.classList.remove('active');
        if (body) body.classList.remove('menu-open');
        if (hamburger) hamburger.setAttribute('aria-expanded', 'false');
      }
    });
  }

  function setupFooterYear() {
    qsa('.js-year').forEach((el) => { el.textContent = String(new Date().getFullYear()); });
  }

  function setupBackToTop() {
    let btn = qs('.back-to-top');
    if (!btn) {
      btn = document.createElement('button');
      btn.className = 'back-to-top';
      btn.type = 'button';
      btn.setAttribute('aria-label', 'العودة للأعلى');
      btn.innerHTML = '<i class="fas fa-arrow-up" aria-hidden="true"></i>';
      document.body.appendChild(btn);
    }

    const toggle = () => btn.classList.toggle('show', window.scrollY > 500);
    toggle();
    window.addEventListener('scroll', toggle, { passive: true });

    btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  function setupProductsDetailsToggles() {
    const showButtons = qsa('[data-show-details]');
    const hideButtons = qsa('[data-hide-details]');
    const isProductsPage = !!qs('#searchInput') && !!qs('.products-section-details');
    if (!isProductsPage) return;

    function showDetails(categoryId) {
      qsa('.products-section-details').forEach((d) => d.classList.remove('active'));
      const target = qs('#' + categoryId);
      if (!target) return;
      target.classList.add('active');
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function hideDetails(categoryId) {
      const target = qs('#' + categoryId);
      if (!target) return;
      target.classList.remove('active');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Backward compatibility with existing inline onclick calls (if any)
    window.showDetails = showDetails;
    window.hideDetails = hideDetails;

    // Optional data-attr hooks (future clean HTML)
    showButtons.forEach((btn) => btn.addEventListener('click', () => showDetails(btn.getAttribute('data-show-details'))));
    hideButtons.forEach((btn) => btn.addEventListener('click', () => hideDetails(btn.getAttribute('data-hide-details'))));

    // Search filtering within product items (products.html)
    const searchInput = qs('#searchInput');
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        const searchTerm = (searchInput.value || '').toLowerCase();
        qsa('.product-item').forEach((item) => {
          const name = item.querySelector('h5')?.textContent?.toLowerCase() || '';
          const desc = item.querySelector('p')?.textContent?.toLowerCase() || '';
          const match = name.includes(searchTerm) || desc.includes(searchTerm);
          item.style.display = match ? 'block' : 'none';
        });
      });
    }
  }

  function setupCategoriesSearchModule() {
    const searchContainer = qs('.search-container');
    const searchInput = qs('#searchInput');
    const categoriesGrid = qs('.categories-grid');

    if (!searchContainer || !searchInput || !categoriesGrid) return;

    // Avoid clashing with products page search filter (products.html)
    if (qs('.product-item')) return;

    let searchResults = qs('.search-results', searchContainer);
    if (!searchResults) {
      searchResults = document.createElement('div');
      searchResults.className = 'search-results';
      searchContainer.appendChild(searchResults);
    }

    searchInput.addEventListener('input', (e) => {
      const searchTerm = (e.target.value || '').trim().toLowerCase();

      if (!searchTerm) {
        searchResults.classList.remove('active');
        categoriesGrid.style.display = 'grid';
        return;
      }

      categoriesGrid.style.display = 'none';

      const categories = qsa('.category-card');
      const filtered = categories.filter((category) => {
        const title = category.querySelector('h3')?.textContent?.toLowerCase() || '';
        return title.includes(searchTerm);
      });

      if (filtered.length) {
        searchResults.innerHTML = filtered.map((category) => {
          const title = escapeHtml(category.querySelector('h3')?.textContent || '');
          const link = category.querySelector('a')?.getAttribute('href') || '#';
          return `<div class="search-result-item" role="button" tabindex="0" data-href="${escapeHtml(link)}">${title}</div>`;
        }).join('');
      } else {
        searchResults.innerHTML = '<div class="search-result-item">لا توجد نتائج</div>';
      }
      searchResults.classList.add('active');
    });

    searchResults.addEventListener('click', (e) => {
      const item = e.target.closest('.search-result-item[data-href]');
      if (!item) return;
      const href = item.getAttribute('data-href');
      if (href) window.location.href = href;
    });

    searchInput.addEventListener('keyup', (e) => {
      if (e.key === 'Escape') {
        searchInput.value = '';
        searchResults.classList.remove('active');
        categoriesGrid.style.display = 'grid';
      }
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.search-container')) {
        searchResults.classList.remove('active');
        if (!searchInput.value) categoriesGrid.style.display = 'grid';
      }
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    setupSmoothAnchors();
    setupRevealOnScroll();
    setupContactForm();

    setupMobileMenu();
    setupNavbarScroll();
    setupFooterYear();
    setupBackToTop();

    // page-specific helpers
    setupProductsDetailsToggles();
    setupCategoriesSearchModule();

    setupFavorites();
  });

  // Favorites System
  function setupFavorites() {
    const favorites = JSON.parse(localStorage.getItem('userFavorites') || '[]');

    // Target ONLY the main image on product details page
    // Using .product-details-grid .main-image as anchor
    const mainImageContainer = qs('.product-details-grid .main-image');

    if (mainImageContainer) {
      const productNameEl = qs('.product-title');
      const name = productNameEl ? productNameEl.textContent.trim() : 'منتج الحالي';

      // Prevent dupes
      if (!qs('.favorite-btn', mainImageContainer)) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'favorite-btn';
        btn.setAttribute('aria-label', 'أضف للمفضلة');
        btn.setAttribute('aria-pressed', favorites.includes(name) ? 'true' : 'false');

        const isFav = favorites.includes(name);
        if (isFav) btn.classList.add('active');

        btn.innerHTML = `<i class="${isFav ? 'fas' : 'far'} fa-heart" aria-hidden="true"></i>`;
        btn.addEventListener('click', (e) => window.toggleFavorite(e, btn, name));
        mainImageContainer.appendChild(btn);
      }
    }

    window.toggleFavorite = function (e, btn, productName) {
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }

      const icon = btn.querySelector('i');
      const isActive = btn.classList.toggle('active');
      btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');

      if (icon) {
        icon.className = isActive ? 'fas fa-heart' : 'far fa-heart';
      }

      let favs = JSON.parse(localStorage.getItem('userFavorites') || '[]');

      if (isActive) {
        if (!favs.includes(productName)) favs.push(productName);
      } else {
        favs = favs.filter(n => n !== productName);
      }

      localStorage.setItem('userFavorites', JSON.stringify(favs));
    };
  }
})();
