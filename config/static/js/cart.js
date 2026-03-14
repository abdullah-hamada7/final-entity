/* Entity Medical - Premium Clean JS
   cart.js: shopping cart
*/
(function () {
  'use strict';

  let cart = [];

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
                <button type="button" onclick="updateQuantity('${safeName}', ${qty - 1})" class="qty-btn">-</button>
                <span class="qty">${qty}</span>
                <button type="button" onclick="updateQuantity('${safeName}', ${qty + 1})" class="qty-btn">+</button>
                <button type="button" onclick="removeFromCart('${safeName}')" class="remove-btn">
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

  function showCartNotification() {
    const notification = document.createElement('div');
    notification.className = 'cart-notification';
    notification.innerHTML = `
      <i class="fas fa-check-circle"></i>
      <span>تم إضافة المنتج للسلة</span>
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

  function addToCart(name, price, icon) {
    const existing = cart.find(item => item.name === name);

    if (existing) {
      existing.quantity = (Number(existing.quantity) || 0) + 1;
    } else {
      cart.push({
        name,
        price: Number(price) || 0,
        icon: icon || 'fas fa-box',
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

  function toggleCart() {
    const cartModal = document.getElementById('cartModal');
    if (!cartModal) return;
    cartModal.classList.toggle('active');
  }

  function checkout() {
    if (!cart.length) {
      alert("عربة المشتريات فارغة");
      return;
    }

    fetch("/orders/submit-cart/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        items: cart
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        clearCart();
        toggleCart();
        showOrderSuccess();
      }
    })
    .catch(() => {
      alert("حدث خطأ أثناء إرسال الطلب");
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    loadCart();
    updateCartUI();

    document.addEventListener('click', (e) => {
      const cartModal = document.getElementById('cartModal');
      if (cartModal && e.target === cartModal) toggleCart();
    });
  });

  window.addToCart = addToCart;
  window.removeFromCart = removeFromCart;
  window.updateQuantity = updateQuantity;
  window.clearCart = clearCart;
  window.toggleCart = toggleCart;
  window.checkout = checkout;

})();