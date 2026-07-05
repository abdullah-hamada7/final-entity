/* Entity Medical - shared client-side form validation */
(function (global) {
  'use strict';

  const PHONE_RE = /^01[0-9]{9}$/;
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const SEARCH_MAX_LEN = 100;
  const SEARCH_MIN_LEN = 2;

  function normalizePhone(value) {
    return String(value || '').trim().replace(/[\s-]/g, '');
  }

  function fieldContainer(input) {
    return input?.closest('.input-group, .form-group, .checkout-field, .search-container, .rating-input');
  }

  function showError(input, message) {
    if (!input) return;
    clearError(input);
    input.classList.add('input-invalid');
    input.setAttribute('aria-invalid', 'true');
    const group = fieldContainer(input);
    if (!group) return;
    const err = document.createElement('span');
    err.className = 'field-error';
    err.setAttribute('role', 'alert');
    err.textContent = message;
    group.appendChild(err);
  }

  function clearError(input) {
    if (!input) return;
    input.classList.remove('input-invalid');
    input.removeAttribute('aria-invalid');
    fieldContainer(input)?.querySelector('.field-error')?.remove();
  }

  function clearFormErrors(form) {
    form.querySelectorAll('.input-invalid').forEach(clearError);
  }

  function validateRequired(value, label) {
    if (!String(value || '').trim()) return `${label} مطلوب`;
    return null;
  }

  function validateName(value) {
    const err = validateRequired(value, 'الاسم');
    if (err) return err;
    const name = String(value).trim();
    if (name.length < 2) return 'الاسم يجب أن يكون حرفين على الأقل';
    if (name.length > 100) return 'الاسم طويل جدًا';
    return null;
  }

  function validatePhone(value, required) {
    const phone = normalizePhone(value);
    if (!phone) return required ? 'رقم الهاتف مطلوب' : null;
    if (!PHONE_RE.test(phone)) return 'أدخل رقم هاتف مصري صحيح (11 رقم يبدأ بـ 01)';
    return null;
  }

  function validateEmail(value, required) {
    const email = String(value || '').trim();
    if (!email) return required ? 'البريد الإلكتروني مطلوب' : null;
    if (email.length > 254) return 'البريد الإلكتروني طويل جدًا';
    if (!EMAIL_RE.test(email)) return 'أدخل بريدًا إلكترونيًا صحيحًا';
    return null;
  }

  function validatePassword(value, minLen) {
    const min = minLen || 6;
    const err = validateRequired(value, 'كلمة المرور');
    if (err) return err;
    if (String(value).length < min) return `كلمة المرور يجب أن تكون ${min} أحرف على الأقل`;
    if (String(value).length > 128) return 'كلمة المرور طويلة جدًا';
    return null;
  }

  function validatePasswordMatch(password, confirm) {
    if (password !== confirm) return 'كلمة المرور غير متطابقة';
    return null;
  }

  function validateSubject(value) {
    const err = validateRequired(value, 'موضوع الرسالة');
    if (err) return err;
    if (String(value).trim().length > 150) return 'موضوع الرسالة طويل جدًا';
    return null;
  }

  function validateMessage(value, minLen) {
    const min = minLen || 10;
    const err = validateRequired(value, 'الرسالة');
    if (err) return err;
    const message = String(value).trim();
    if (message.length < min) return `الرسالة يجب أن تكون ${min} أحرف على الأقل`;
    if (message.length > 2000) return 'الرسالة طويلة جدًا';
    return null;
  }

  function validateAddress(value) {
    const err = validateRequired(value, 'العنوان');
    if (err) return err;
    if (String(value).trim().length < 5) return 'العنوان قصير جدًا';
    return null;
  }

  function validateSearchQuery(value) {
    const query = String(value || '').trim();
    if (!query) return null;
    if (query.length < SEARCH_MIN_LEN) {
      return `كلمة البحث يجب أن تكون ${SEARCH_MIN_LEN} أحرف على الأقل`;
    }
    if (query.length > SEARCH_MAX_LEN) {
      return `كلمة البحث طويلة جدًا (${SEARCH_MAX_LEN} حرف كحد أقصى)`;
    }
    return null;
  }

  function bindLiveClear(form) {
    form.querySelectorAll('input, textarea, select').forEach((input) => {
      input.addEventListener('input', () => clearError(input));
      input.addEventListener('change', () => clearError(input));
    });
  }

  function bindForm(form, validateFn) {
    if (!form) return;
    bindLiveClear(form);
    form.addEventListener('submit', (e) => {
      clearFormErrors(form);
      const result = validateFn(form);
      if (result !== true) {
        e.preventDefault();
        if (result && result.input && result.message) {
          showError(result.input, result.message);
          result.input.focus();
        }
      }
    });
  }

  function fail(input, message) {
    return { input, message };
  }

  function bindSearchForm(form, inputSelector) {
    bindForm(form, (searchForm) => {
      const search = searchForm.querySelector(inputSelector || 'input[name="search"], .search-input');
      let msg = validateSearchQuery(search?.value);
      if (msg) return fail(search, msg);
      if (search) search.value = String(search.value).trim();
      return true;
    });
  }

  function setupAuthForms() {
    bindForm(document.getElementById('loginForm'), (form) => {
      const phone = form.querySelector('#loginPhone');
      const password = form.querySelector('#loginPassword');
      let msg = validatePhone(phone?.value, true);
      if (msg) return fail(phone, msg);
      msg = validatePassword(password?.value, 6);
      if (msg) return fail(password, msg);
      return true;
    });

    bindForm(document.getElementById('signupForm'), (form) => {
      const name = form.querySelector('#signupName');
      const phone = form.querySelector('#signupPhone');
      const email = form.querySelector('#signupEmail');
      const password = form.querySelector('#signupPassword');
      const confirm = form.querySelector('#signupPassword2');
      let msg = validateName(name?.value);
      if (msg) return fail(name, msg);
      msg = validatePhone(phone?.value, true);
      if (msg) return fail(phone, msg);
      msg = validateEmail(email?.value, false);
      if (msg) return fail(email, msg);
      msg = validatePassword(password?.value, 6);
      if (msg) return fail(password, msg);
      msg = validatePasswordMatch(password?.value, confirm?.value);
      if (msg) return fail(confirm, msg);
      return true;
    });

    bindForm(document.getElementById('resetForm'), (form) => {
      const phone = form.querySelector('#resetPhone');
      const password = form.querySelector('#resetPassword');
      const confirm = form.querySelector('#resetPassword2');
      let msg = validatePhone(phone?.value, true);
      if (msg) return fail(phone, msg);
      msg = validatePassword(password?.value, 6);
      if (msg) return fail(password, msg);
      msg = validatePasswordMatch(password?.value, confirm?.value);
      if (msg) return fail(confirm, msg);
      return true;
    });

    bindForm(document.getElementById('profileForm'), (form) => {
      const name = form.querySelector('#profileName');
      const email = form.querySelector('#profileEmail');
      const newPassword = form.querySelector('#newPassword');
      let msg = validateName(name?.value);
      if (msg) return fail(name, msg);
      msg = validateEmail(email?.value, false);
      if (msg) return fail(email, msg);
      if (newPassword?.value) {
        msg = validatePassword(newPassword.value, 6);
        if (msg) return fail(newPassword, msg);
      }
      return true;
    });

    bindForm(document.getElementById('contactForm'), (form) => {
      const name = form.querySelector('#name');
      const email = form.querySelector('#email');
      const phone = form.querySelector('#phone');
      const subject = form.querySelector('#subject');
      const message = form.querySelector('#message');
      let msg = validateName(name?.value);
      if (msg) return fail(name, msg);
      msg = validateEmail(email?.value, true);
      if (msg) return fail(email, msg);
      msg = validatePhone(phone?.value, true);
      if (msg) return fail(phone, msg);
      msg = validateSubject(subject?.value);
      if (msg) return fail(subject, msg);
      msg = validateMessage(message?.value, 10);
      if (msg) return fail(message, msg);
      return true;
    });
  }

    function setupSearchForms() {
    bindSearchForm(document.getElementById('productsSearchForm'), '#searchInput');
    bindSearchForm(document.getElementById('categorySearchForm'), '#categorySearchInput');
  }

  function validateReviewRating(form) {
    const selected = form.querySelector('input[name="rating"]:checked');
    if (!selected) return 'اختر تقييمًا من 1 إلى 5';
    return null;
  }

  function setupReviewForm() {
    const form = document.getElementById('reviewForm');
    if (!form) return;

    bindLiveClear(form);
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearFormErrors(form);

      const comment = form.querySelector('#reviewComment');
      let msg = validateReviewRating(form);
      if (msg) {
        const group = form.querySelector('#reviewRatingGroup');
        showError(group, msg);
        return;
      }
      msg = validateMessage(comment?.value, 3);
      if (msg) {
        showError(comment, msg);
        comment?.focus();
        return;
      }
      if (String(comment?.value || '').trim().length > 1000) {
        showError(comment, 'التعليق طويل جدًا');
        comment?.focus();
        return;
      }

      const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
      const submitBtn = form.querySelector('[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          credentials: 'same-origin',
          headers: {
            Accept: 'application/json',
            'X-CSRFToken': csrfToken,
          },
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok && data.success) {
          form.reset();
          clearFormErrors(form);
          if (global.EntityNotify?.show) {
            global.EntityNotify.show(data.message || 'تم إرسال التقييم بنجاح', 'success');
          }
          return;
        }

        const errorMessage = data.message || 'تعذر إرسال التقييم';
        if (global.EntityNotify?.show) {
          global.EntityNotify.show(errorMessage, 'error');
        }
      } catch (_err) {
        if (global.EntityNotify?.show) {
          global.EntityNotify.show('تعذر إرسال التقييم', 'error');
        }
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  function initValidation() {
    setupAuthForms();
    setupSearchForms();
    setupReviewForm();
  }

  document.addEventListener('DOMContentLoaded', initValidation);

  global.EntityValidation = {
    showError,
    clearError,
    clearFormErrors,
    validateName,
    validatePhone,
    validateEmail,
    validatePassword,
    validatePasswordMatch,
    validateMessage,
    validateAddress,
    validateSearchQuery,
    normalizePhone,
  };
})(window);
