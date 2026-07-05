/* Entity Medical - Premium Clean JS
   cart.js: shopping cart (synced with backend API)
*/
(function () {
  'use strict';

  const API = {
    cart: '/orders/api/cart/',
    add: '/orders/api/cart/add/',
    update: '/orders/api/cart/update/',
    remove: '/orders/api/cart/remove/',
    clear: '/orders/api/cart/clear/',
    checkout: '/orders/api/orders/create/',
  };

  let cart = [];
  let previousFocus = null;
  let cartReady = false;

  function isLoggedIn() {
    return document.body?.dataset.auth === 'true';
  }

  function getLoginUrl() {
    const base = document.body?.dataset.loginUrl || '/users/login/';
    const next = encodeURIComponent(window.location.pathname + window.location.search);
    return `${base}?next=${next}`;
  }

  function notify(message, type = 'info', duration) {
    if (window.EntityNotify?.show) {
      window.EntityNotify.show(message, type, duration);
      return;
    }
    const fallback = document.createElement('div');
    fallback.className = 'app-toast app-toast--error show';
    fallback.setAttribute('role', 'alert');
    fallback.textContent = message;
    document.body.appendChild(fallback);
    setTimeout(() => fallback.remove(), 3000);
  }

  function redirectToLogin(message) {
    if (message) notify(message, 'warning');
    setTimeout(() => {
      window.location.href = getLoginUrl();
    }, message ? 1200 : 0);
  }

  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content') || '';
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  function money(n) {
    const num = Number(n || 0);
    if (!Number.isFinite(num)) return '0';
    return String(Math.round(num));
  }

  function applyCartPayload(cartData) {
    if (!cartData?.items) {
      cart = [];
      return;
    }

    cart = cartData.items.map((item) => ({
      cartItemId: item.id,
      productId: item.product?.id,
      name: item.product?.name || '',
      price: Number(item.product?.final_price ?? item.product?.price ?? 0),
      icon: item.product?.icon || 'fas fa-box',
      quantity: Number(item.quantity) || 1,
    }));
  }

  async function apiRequest(url, method, body) {
    const headers = { 'Content-Type': 'application/json' };
    const csrfToken = getCsrfToken();
    if (csrfToken) headers['X-CSRFToken'] = csrfToken;

    const options = {
      method,
      headers,
      credentials: 'same-origin',
    };

    if (body !== undefined) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));
    return { ok: response.ok, status: response.status, data };
  }

  async function syncCartFromServer() {
    const { ok, data } = await apiRequest(API.cart, 'GET');
    if (ok && data.success && data.cart) {
      applyCartPayload(data.cart);
      return true;
    }
    cart = [];
    return false;
  }

  async function migrateLocalStorageCart() {
    let saved = null;
    try {
      saved = localStorage.getItem('medicalCart');
    } catch (_e) {
      return;
    }

    if (!saved) return;

    let legacyItems = [];
    try {
      legacyItems = JSON.parse(saved);
    } catch (_e) {
      localStorage.removeItem('medicalCart');
      return;
    }

    if (!Array.isArray(legacyItems) || !legacyItems.length) {
      localStorage.removeItem('medicalCart');
      return;
    }

    for (const item of legacyItems) {
      const productId = item.productId || item.product_id;
      if (!productId) continue;
      await apiRequest(API.add, 'POST', {
        product_id: productId,
        quantity: Number(item.quantity) || 1,
      });
    }

    localStorage.removeItem('medicalCart');
  }

  function updateCheckoutButton() {
    const btn = document.getElementById('cartCheckoutBtn');
    const notice = document.getElementById('cartLoginNotice');
    const loggedIn = isLoggedIn();

    if (btn) {
      btn.textContent = loggedIn ? 'إتمام الطلب' : 'تسجيل الدخول لإتمام الطلب';
    }
    if (notice) {
      notice.hidden = loggedIn;
    }
  }

  function getCheckoutDetails() {
    const body = document.body;
    const validation = window.EntityValidation;

    return {
      full_name: body.dataset.userName || '',
      phone: validation ? validation.normalizePhone(body.dataset.userPhone) : (body.dataset.userPhone || ''),
      email: body.dataset.userEmail || '',
      address: '',
      notes: '',
    };
  }

  function updateCartUI() {
    const cartCounts = document.querySelectorAll('.cart-count');
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');

    if (cartCounts.length) {
      const totalItems = cart.reduce((sum, item) => sum + (Number(item.quantity) || 0), 0);
      cartCounts.forEach((el) => { el.textContent = String(totalItems); });
    }

    if (cartItems) {
      if (!cart.length) {
        cartItems.innerHTML = `
          <div class="empty-cart">
            <i class="fas fa-shopping-cart"></i>
            <p>عربة المشتريات فارغة</p>
          </div>
        `;
      } else {
        cartItems.innerHTML = cart.map((item) => {
          const icon = item.icon || 'fas fa-box';
          const qty = Number(item.quantity) || 1;
          const price = Number(item.price) || 0;
          const itemId = Number(item.cartItemId);

          return `
            <div class="cart-item">
              <div class="item-icon"><i class="${icon}"></i></div>
              <div class="item-details">
                <h4>${item.name}</h4>
                <p class="item-price">${money(price)} جنيه</p>
              </div>
              <div class="item-controls">
                <button type="button" onclick="updateQuantity(${itemId}, ${qty - 1})" class="qty-btn" aria-label="تقليل الكمية">-</button>
                <span class="qty">${qty}</span>
                <button type="button" onclick="updateQuantity(${itemId}, ${qty + 1})" class="qty-btn" aria-label="زيادة الكمية">+</button>
                <button type="button" onclick="removeFromCart(${itemId})" class="remove-btn" aria-label="حذف المنتج">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          `;
        }).join('');
      }
    }

    if (cartTotal) {
      const total = cart.reduce((sum, item) =>
        sum + ((Number(item.price) || 0) * (Number(item.quantity) || 0)), 0);
      cartTotal.textContent = `${money(total)} جنيه`;
    }

    updateCheckoutButton();
  }

  function showCartNotification(message = 'تم إضافة المنتج للسلة') {
    notify(message, 'success', 2500);
  }

  function showOrderSuccess() {
    notify('تم استلام طلبك وسوف يتم التواصل معك قريبًا', 'success', 3000);
  }

  async function addToCart(name, price, icon, productId) {
    if (!productId) {
      notify('لا يمكن إضافة هذا المنتج', 'error');
      return;
    }

    const { ok, data } = await apiRequest(API.add, 'POST', {
      product_id: productId,
      quantity: 1,
    });

    if (ok && data.success && data.cart) {
      applyCartPayload(data.cart);
      updateCartUI();
      showCartNotification();
      return;
    }

    notify(data.message || data.errors?.product_id?.[0] || 'فشل إضافة المنتج', 'error');
  }

  async function removeFromCart(cartItemId) {
    const { ok, data } = await apiRequest(API.remove, 'DELETE', { item_id: cartItemId });

    if (ok && data.success && data.cart) {
      applyCartPayload(data.cart);
      updateCartUI();
      return;
    }

    notify(data.message || 'فشل حذف المنتج', 'error');
  }

  async function updateQuantity(cartItemId, newQty) {
    const qty = Number(newQty) || 0;

    const { ok, data } = await apiRequest(API.update, 'PUT', {
      item_id: cartItemId,
      quantity: qty,
    });

    if (ok && data.success && data.cart) {
      applyCartPayload(data.cart);
      updateCartUI();
      return;
    }

    notify(data.message || 'فشل تحديث الكمية', 'error');
  }

  async function clearCart() {
    const { ok, data } = await apiRequest(API.clear, 'POST');

    if (ok && data.success) {
      cart = [];
      updateCartUI();
      notify('تم تفريغ السلة', 'info');
      return;
    }

    notify(data.message || 'فشل تفريغ السلة', 'error');
  }

  function toggleCart(forceOpen) {
    const cartModal = document.getElementById('cartModal');
    if (!cartModal) return;

    const shouldOpen = typeof forceOpen === 'boolean'
      ? forceOpen
      : !cartModal.classList.contains('active');

    if (shouldOpen) {
      previousFocus = document.activeElement;
      cartModal.classList.add('active');
      document.body.classList.add('cart-open');
      updateCheckoutButton();
      cartModal.querySelector('.close-cart')?.focus();
    } else {
      cartModal.classList.remove('active');
      document.body.classList.remove('cart-open');
      if (previousFocus && typeof previousFocus.focus === 'function') {
        previousFocus.focus();
      }
      previousFocus = null;
    }
  }

  async function checkout() {
    if (!cart.length) {
      notify('عربة المشتريات فارغة', 'warning');
      return;
    }

    if (!isLoggedIn()) {
      redirectToLogin('يجب تسجيل الدخول لإتمام الطلب');
      return;
    }

    const details = getCheckoutDetails();
    const { ok, status, data } = await apiRequest(API.checkout, 'POST', details);

    if (status === 401 || status === 403) {
      redirectToLogin('يجب تسجيل الدخول لإتمام الطلب');
      return;
    }

    if (ok && data.success) {
      cart = [];
      updateCartUI();
      toggleCart(false);
      showOrderSuccess();
      if (data.whatsapp_link) {
        setTimeout(() => window.open(data.whatsapp_link, '_blank'), 800);
      }
      return;
    }

    notify(data.message || 'حدث خطأ أثناء إرسال الطلب', 'error');
  }

  async function addAllToCart() {
    const productCards = document.querySelectorAll('.offer-detail-section .product-card');
    if (!productCards.length) {
      notify('لا توجد منتجات لإضافتها', 'warning');
      return;
    }

    let addedCount = 0;

    for (const card of productCards) {
      const productId = card.getAttribute('data-product-id');
      if (!productId) continue;

      const nameElement = card.querySelector('h3');
      const name = nameElement?.textContent?.trim() || '';
      const alreadyInCart = cart.some((item) => item.name === name);
      if (alreadyInCart) continue;

      const { ok, data } = await apiRequest(API.add, 'POST', {
        product_id: Number(productId),
        quantity: 1,
      });

      if (ok && data.success && data.cart) {
        applyCartPayload(data.cart);
        addedCount += 1;
      }
    }

    updateCartUI();

    if (addedCount > 0) {
      showCartNotification(`تم إضافة ${addedCount} منتج للسلة بنجاح!`);
      setTimeout(() => toggleCart(true), 500);
    } else {
      notify('جميع المنتجات موجودة بالفعل في السلة', 'info');
    }
  }

  function trapCartFocus(e) {
    const cartModal = document.getElementById('cartModal');
    if (!cartModal || !cartModal.classList.contains('active') || e.key !== 'Tab') return;

    const focusable = cartModal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (!focusable.length) return;

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  async function initCart() {
    await syncCartFromServer();
    await migrateLocalStorageCart();
    await syncCartFromServer();
    cartReady = true;
    updateCartUI();
  }

  document.addEventListener('DOMContentLoaded', () => {
    initCart().catch(() => {
      cart = [];
      updateCartUI();
    });

    document.addEventListener('click', (e) => {
      const cartModal = document.getElementById('cartModal');
      if (cartModal && e.target === cartModal) toggleCart(false);
    });

    document.addEventListener('keydown', (e) => {
      const cartModal = document.getElementById('cartModal');
      if (e.key === 'Escape' && cartModal?.classList.contains('active')) {
        toggleCart(false);
      }
      trapCartFocus(e);
    });
  });

  window.addToCart = addToCart;
  window.removeFromCart = removeFromCart;
  window.updateQuantity = updateQuantity;
  window.clearCart = clearCart;
  window.toggleCart = toggleCart;
  window.checkout = checkout;
  window.addAllToCart = addAllToCart;

})();
