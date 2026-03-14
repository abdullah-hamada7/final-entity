/* Entity Medical - product-details.js
   Requires: products-data.js + cart.js (for addToCart)
*/
(function () {
  'use strict';

  const qs = (sel, root = document) => root.querySelector(sel);
  const qsa = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const products = window.PRODUCTS_DATA || {};

  function getProductId() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('product') || 'ecg';
  }

  function parsePrice(priceText) {
    const digits = String(priceText || '').replace(/[^\d]/g, '');
    const n = parseInt(digits, 10);
    return Number.isFinite(n) ? n : 0;
  }

  function updateProductDetails(productId) {
    const product = products[productId];
    if (!product) return;

    qs('#product-title') && (qs('#product-title').textContent = product.title);
    qs('#product-brand') && (qs('#product-brand').textContent = product.brand);
    qs('#product-price') && (qs('#product-price').textContent = product.price);
    qs('#product-description') && (qs('#product-description').textContent = product.description);

    // Update Back Link to point to Category
    const backLink = qs('.back-link');
    if (backLink && product.categoryUrl) {
      backLink.href = product.categoryUrl;
      backLink.innerHTML = '<i class="fas fa-arrow-right"></i> العودة إلى منتجات القسم';
    }

    const featuresList = qs('#product-features');
    if (featuresList) {
      featuresList.innerHTML = '';
      (product.features || []).forEach((feature) => {
        const li = document.createElement('li');
        li.innerHTML = `<i class="fas fa-check" aria-hidden="true"></i> ${feature}`;
        featuresList.appendChild(li);
      });
    }

    const mainIcon = qs('#main-product-icon');
    if (mainIcon) mainIcon.className = product.icon;

    document.title = `${product.title} | Entity Medical`;
  }

  function createThumbnails(count = 10) {
    const grid = qs('#thumbnailGrid');
    if (!grid) return;

    // Image paths from products/1488 folder
    const imagePaths = [
      'images/products/1488/1.webp',
      'images/products/1488/2.jpg',
      'images/products/1488/3.jpg',
      'images/products/1488/4.jpg',
      'images/products/1488/5.jpg',
      'images/products/1488/6.jpg',
      'images/products/1488/7.jpg',
      'images/products/1488/8.jpg',
      'images/products/1488/9.webp',
      'images/products/1488/10.jpg'
    ];

    grid.innerHTML = '';
    const totalImages = Math.min(count, imagePaths.length);

    for (let i = 0; i < totalImages; i++) {
      const thumb = document.createElement('div');
      thumb.className = 'thumbnail';
      if (i === 0) thumb.classList.add('active');
      thumb.setAttribute('data-image-src', imagePaths[i]);
      thumb.setAttribute('data-index', String(i));

      const img = document.createElement('img');
      img.src = imagePaths[i];
      img.alt = `صورة المنتج ${i + 1}`;
      img.className = 'thumbnail-image';

      thumb.appendChild(img);
      grid.appendChild(thumb);
    }

    const countEl = qs('#thumbnailCount');
    if (countEl) countEl.textContent = `${totalImages} صور`;

    // Set first image as main image
    if (imagePaths.length > 0) {
      const mainImageContainer = qs('.main-image');
      if (mainImageContainer) {
        const mainIcon = qs('#main-product-icon');
        if (mainIcon) mainIcon.style.display = 'none';

        let mainImg = qs('#main-product-img');
        if (!mainImg) {
          mainImg = document.createElement('img');
          mainImg.id = 'main-product-img';
          mainImg.className = 'main-product-image';
          mainImageContainer.appendChild(mainImg);
        }
        mainImg.src = imagePaths[0];
        mainImg.alt = 'صورة المنتج الرئيسية';
        mainImg.style.display = 'block';
      }
    }
  }

  function setupThumbnailClick() {
    const grid = qs('#thumbnailGrid');
    if (!grid) return;

    grid.addEventListener('click', (e) => {
      const thumb = e.target.closest('.thumbnail');
      if (!thumb) return;

      qsa('.thumbnail', grid).forEach((t) => t.classList.remove('active'));
      thumb.classList.add('active');

      const imageSrc = thumb.getAttribute('data-image-src');
      if (!imageSrc) return;

      const mainImageContainer = qs('.main-image');
      if (!mainImageContainer) return;

      // Hide icon if exists
      const mainIcon = qs('#main-product-icon');
      if (mainIcon) mainIcon.style.display = 'none';

      // Update or create main image
      let mainImg = qs('#main-product-img');
      if (!mainImg) {
        mainImg = document.createElement('img');
        mainImg.id = 'main-product-img';
        mainImg.className = 'main-product-image';
        mainImageContainer.appendChild(mainImg);
      }
      mainImg.src = imageSrc;
      mainImg.alt = 'صورة المنتج';
      mainImg.style.display = 'block';
    });
  }

  function goToProduct(productId) {
    window.location.href = `product-details.html?product=${encodeURIComponent(productId)}`;
  }

  function addToCartFromDetails() {
    const product = products[getProductId()];
    if (!product) return;
    const price = parsePrice(product.price);
    const icon = product.icon || 'fas fa-box';
    if (typeof window.addToCart === 'function') window.addToCart(product.title, price, icon);
  }

  document.addEventListener('DOMContentLoaded', () => {
    const pid = getProductId();
    createThumbnails(10); // Updated to 10 images
    updateProductDetails(pid);
    setupThumbnailClick();
  });

  window.goToProduct = goToProduct;
  window.addToCartFromDetails = addToCartFromDetails;
})();
