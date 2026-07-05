/* Entity Medical - Profile page helpers */
(function () {
  'use strict';

  const ORDERS_API = '/orders/api/orders/';

  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content') || '';
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  function formatMoney(value) {
    const num = Number(value || 0);
    if (!Number.isFinite(num)) return '0';
    return String(Math.round(num));
  }

  function formatDate(isoDate) {
    if (!isoDate) return '';
    const date = new Date(isoDate);
    if (Number.isNaN(date.getTime())) return isoDate;
    return date.toLocaleString('ar-EG', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  function escapeHtml(text) {
    return String(text || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

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

  function renderOrders(orders) {
    const listEl = document.getElementById('profileOrdersList');
    const emptyEl = document.getElementById('profileOrdersEmpty');
    const loadingEl = document.getElementById('profileOrdersLoading');
    const statOrders = document.getElementById('statOrders');

    if (loadingEl) loadingEl.hidden = true;

    if (statOrders) {
      statOrders.textContent = String(Array.isArray(orders) ? orders.length : 0);
    }

    if (!listEl || !emptyEl) return;

    if (!Array.isArray(orders) || !orders.length) {
      listEl.hidden = true;
      emptyEl.hidden = false;
      return;
    }

    listEl.hidden = false;
    emptyEl.hidden = true;

    listEl.innerHTML = orders.map((order) => {
      const status = escapeHtml(order.status || 'pending');
      const statusLabel = escapeHtml(order.status_display || order.status || '');
      const items = Array.isArray(order.items) ? order.items : [];
      const itemsHtml = items.map((item) =>
        `<li>${escapeHtml(item.product_name)} × ${Number(item.quantity) || 0}</li>`
      ).join('');

      return `
        <div class="order-item">
          <div class="order-item-header">
            <strong>طلب #${escapeHtml(order.order_number)}</strong>
            <span class="order-status order-status--${status}">${statusLabel}</span>
          </div>
          <div class="order-item-meta">
            <span><i class="fas fa-calendar"></i> ${formatDate(order.created_at)}</span>
            <span><i class="fas fa-coins"></i> ${formatMoney(order.total_amount)} جنيه</span>
          </div>
          <ul class="order-item-products">${itemsHtml}</ul>
        </div>
      `;
    }).join('');
  }

  function showOrdersError(message) {
    const loadingEl = document.getElementById('profileOrdersLoading');
    const errorEl = document.getElementById('profileOrdersError');
    if (loadingEl) loadingEl.hidden = true;
    if (errorEl) {
      errorEl.hidden = false;
      const msg = errorEl.querySelector('[data-orders-error]');
      if (msg) msg.textContent = message;
    }
  }

  async function loadProfileOrders() {
    const panel = document.getElementById('profileOrdersPanel');
    if (!panel) return;

    try {
      const response = await fetch(ORDERS_API, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
          'X-CSRFToken': getCsrfToken(),
        },
      });

      const data = await response.json().catch(() => ({}));

      if (response.status === 401 || response.status === 403) {
        showOrdersError('يجب تسجيل الدخول لعرض الطلبات');
        return;
      }

      if (!response.ok || !data.success) {
        showOrdersError(data.message || 'تعذر تحميل الطلبات');
        return;
      }

      renderOrders(data.orders || []);
    } catch (_e) {
      showOrdersError('تعذر تحميل الطلبات');
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    initProfileStats();
    loadProfileOrders();
  });
})();
