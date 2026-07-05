/* Entity Medical - Profile page helpers */
(function () {
  'use strict';

  function getOrdersApiUrl() {
    const panel = document.getElementById('profileOrdersPanel');
    return panel?.dataset.ordersApi || '/orders/api/orders/';
  }

  function hideLoading() {
    const loadingEl = document.getElementById('profileOrdersLoading');
    if (loadingEl) loadingEl.hidden = true;
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
    const errorEl = document.getElementById('profileOrdersError');
    const statOrders = document.getElementById('statOrders');

    hideLoading();

    if (errorEl) errorEl.hidden = true;

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
    const emptyEl = document.getElementById('profileOrdersEmpty');
    const listEl = document.getElementById('profileOrdersList');
    const errorEl = document.getElementById('profileOrdersError');

    hideLoading();

    if (listEl) listEl.hidden = true;
    if (emptyEl) emptyEl.hidden = true;
    if (errorEl) {
      errorEl.hidden = false;
      const msg = errorEl.querySelector('[data-orders-error]');
      if (msg) msg.textContent = message;
    }
  }

  async function loadProfileOrders() {
    const panel = document.getElementById('profileOrdersPanel');
    if (!panel) return;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    try {
      const response = await fetch(getOrdersApiUrl(), {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
          Accept: 'application/json',
        },
        signal: controller.signal,
      });

      const data = await response.json().catch(() => ({}));

      if (response.status === 401 || response.status === 403) {
        showOrdersError('يجب تسجيل الدخول لعرض الطلبات');
        return;
      }

      if (!response.ok || data.success !== true) {
        showOrdersError(data.message || 'تعذر تحميل الطلبات');
        return;
      }

      renderOrders(data.orders || []);
    } catch (err) {
      if (err?.name === 'AbortError') {
        showOrdersError('انتهت مهلة تحميل الطلبات');
      } else {
        showOrdersError('تعذر تحميل الطلبات');
      }
    } finally {
      clearTimeout(timeoutId);
      hideLoading();
    }
  }

  function initProfilePage() {
    initProfileStats();
    loadProfileOrders();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initProfilePage);
  } else {
    initProfilePage();
  }
})();
