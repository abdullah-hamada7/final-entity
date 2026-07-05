/* Entity Medical - Premium Clean JS
   cart.js: shopping cart
*/
(function () {
  'use strict';

  let cart = [];
  let previousFocus = null;

  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content') || '';
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  function loadCart() {
    try {
      const saved = localStorage.getItem('medicalCart');
      cart = saved ? JSON.parse(saved) : [];
      if (!Array.isArray(cart)) cart = [];
    } catch (_e) {
      cart = [];
    }
  }

  function saveCart() {
    localStorage.setItem('medicalCart', JSON.stringify(cart));
  }

  function money(n) {
    const num = Number(n || 0);
    if (!Number.isFinite(num)) return '0';
    return String(num);
  }

  function updateCartUI() {
    const cartCounts = document.querySelectorAll('.cart-count');
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');

    if (cartCounts.length) {
      const totalItems = cart.reduce((sum, item) => sum + (Number(item.quantity) || 0), 0);
      cartCounts.forEach(el => el.textContent = String(totalItems));
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
          const safeName = String(item.name || '').replace(/'/g, "\\'");

          return `
            <div class="cart-item">
              <div class="item-icon"><i class="${icon}"></i></div>
              <div class="item-details">
                <h4>${item.name}</h4>
                <p class="item-price">${money(price)} جنيه</p>
              </div>
              <div class="item-controls">
                <button type="button" onclick="updateQuantity('${safeName}', ${qty - 1})" class="qty-btn" aria-label="تقليل الكمية">-</button>
                <span class="qty">${qty}</span>
                <button type="button" onclick="updateQuantity('${safeName}', ${qty + 1})" class="qty-btn" aria-label="زيادة الكمية">+</button>
                <button type="button" onclick="removeFromCart('${safeName}')" class="remove-btn" aria-label="حذف المنتج">
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
        sum + ((Number(item.price) || 0) * (Number(item.quantity) || 0)), 0
      );
      cartTotal.textContent = `${money(total)} جنيه`;
    }
  }

  function showCartNotification(message = 'تم إضافة المنتج للسلة') {
    const notification = document.createElement('div');
    notification.className = 'cart-notification';
    notification.innerHTML = `
      <i class="fas fa-check-circle"></i>
      <span>${message}</span>
    `;
    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add('show'), 60);
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 250);
    }, 2500);
  }

  function showOrderSuccess() {
    const notification = document.createElement('div');
    notification.className = 'cart-notification';
    notification.innerHTML = `
      <i class="fas fa-check-circle"></i>
      <span>تم استلام طلبك وسوف يتم التواصل معك قريبًا</span>
    `;
    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add('show'), 60);
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 250);
    }, 3000);
  }

  function addToCart(name, price, icon, productId) {
    const existing = cart.find(item => item.name === name);

    if (existing) {
      existing.quantity = (Number(existing.quantity) || 0) + 1;
    } else {
      cart.push({
        name,
        price: Number(price) || 0,
        icon: (typeof icon === 'string' && icon) ? icon : 'fas fa-box',
        productId: productId || null,
        quantity: 1
      });
    }

    saveCart();
    updateCartUI();
    showCartNotification();
  }

  function removeFromCart(name) {
    cart = cart.filter(item => item.name !== name);
    saveCart();
    updateCartUI();
  }

  function updateQuantity(name, newQty) {
    const item = cart.find(it => it.name === name);
    if (!item) return;

    const qty = Number(newQty) || 0;
    if (qty <= 0) return removeFromCart(name);

    item.quantity = qty;
    saveCart();
    updateCartUI();
  }

  function clearCart() {
    cart = [];
    saveCart();
    updateCartUI();
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
      const closeBtn = cartModal.querySelector('.close-cart');
      closeBtn?.focus();
    } else {
      cartModal.classList.remove('active');
      document.body.classList.remove('cart-open');
      if (previousFocus && typeof previousFocus.focus === 'function') {
        previousFocus.focus();
      }
      previousFocus = null;
    }
  }

  function prefillCheckoutFields() {
    const body = document.body;
    const nameInput = document.getElementById('checkoutName');
    const phoneInput = document.getElementById('checkoutPhone');
    if (!nameInput || !phoneInput) return;

    if (body.dataset.auth === 'true') {
      if (!nameInput.value) nameInput.value = body.dataset.userName || '';
      if (!phoneInput.value) phoneInput.value = body.dataset.userPhone || '';
    }
  }

  function checkout() {
    if (!cart.length) {
      alert("عربة المشتريات فارغة");
      return;
    }

    prefillCheckoutFields();

    const nameInput = document.getElementById('checkoutName');
    const phoneInput = document.getElementById('checkoutPhone');
    const addressInput = document.getElementById('checkoutAddress');
    const validation = window.EntityValidation;

    if (validation) {
      validation.clearFormErrors(document.getElementById('checkoutFields'));
      let msg = validation.validateName(nameInput?.value);
      if (msg) {
        validation.showError(nameInput, msg);
        nameInput.focus();
        return;
      }
      msg = validation.validatePhone(phoneInput?.value, true);
      if (msg) {
        validation.showError(phoneInput, msg);
        phoneInput.focus();
        return;
      }
    }

    const headers = {
      "Content-Type": "application/json",
    };
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      headers["X-CSRFToken"] = csrfToken;
    }

    fetch("/orders/submit-cart/", {
      method: "POST",
      headers,
      credentials: "same-origin",
      body: JSON.stringify({
        items: cart,
        full_name: nameInput?.value?.trim(),
        phone: validation ? validation.normalizePhone(phoneInput?.value) : phoneInput?.value?.trim(),
        address: addressInput?.value?.trim() || '',
        email: document.body.dataset.userEmail || '',
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        clearCart();
        toggleCart(false);
        showOrderSuccess();
        if (data.whatsapp_link) {
          setTimeout(() => window.open(data.whatsapp_link, '_blank'), 800);
        }
      } else {
        alert(data.message || "حدث خطأ أثناء إرسال الطلب");
      }
    })
    .catch(() => {
      alert("حدث خطأ أثناء إرسال الطلب");
    });
  }

  function addAllToCart() {
    const productCards = document.querySelectorAll('.offer-detail-section .product-card');
    if (!productCards.length) {
      alert('لا توجد منتجات لإضافتها');
      return;
    }

    let addedCount = 0;

    productCards.forEach((card) => {
      const nameElement = card.querySelector('h3');
      const priceElement = card.querySelector('.offer-price');
      const productId = card.getAttribute('data-product-id');

      if (!nameElement || !priceElement) return;

      const name = nameElement.textContent.trim();
      const priceText = priceElement.textContent.replace(/[^\d.]/g, '');
      const price = parseFloat(priceText) || 0;

      const existing = cart.find((item) => item.name === name);
      if (!existing) {
        cart.push({
          name,
          price,
          icon: 'fas fa-box',
          quantity: 1,
          productId: productId || null
        });
        addedCount++;
      }
    });

    if (addedCount > 0) {
      saveCart();
      updateCartUI();
      showCartNotification(`تم إضافة ${addedCount} منتج للسلة بنجاح!`);
      setTimeout(() => toggleCart(true), 500);
    } else {
      alert('جميع المنتجات موجودة بالفعل في السلة');
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

  document.addEventListener('DOMContentLoaded', () => {
    loadCart();
    updateCartUI();

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
