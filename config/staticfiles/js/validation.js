/* Entity Medical - shared client-side form validation */
(function (global) {
  'use strict';

  const PHONE_RE = /^01[0-9]{9}$/;
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function normalizePhone(value) {
    return String(value || '').trim().replace(/[\s-]/g, '');
  }

  function showError(input, message) {
    if (!input) return;
    clearError(input);
    input.classList.add('input-invalid');
    input.setAttribute('aria-invalid', 'true');
    const group = input.closest('.input-group, .form-group, .checkout-field');
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
    input.closest('.input-group, .form-group, .checkout-field')?.querySelector('.field-error')?.remove();
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
    if (String(value).trim().length < 2) return 'الاسم يجب أن يكون حرفين على الأقل';
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
    if (!EMAIL_RE.test(email)) return 'أدخل بريدًا إلكترونيًا صحيحًا';
    return null;
  }

  function validatePassword(value, minLen) {
    const min = minLen || 6;
    const err = validateRequired(value, 'كلمة المرور');
    if (err) return err;
    if (String(value).length < min) return `كلمة المرور يجب أن تكون ${min} أحرف على الأقل`;
    return null;
  }

  function validatePasswordMatch(password, confirm) {
    if (password !== confirm) return 'كلمة المرور غير متطابقة';
    return null;
  }

  function validateSubject(value) {
    return validateRequired(value, 'موضوع الرسالة');
  }

  function validateMessage(value, minLen) {
    const min = minLen || 10;
    const err = validateRequired(value, 'الرسالة');
    if (err) return err;
    if (String(value).trim().length < min) return `الرسالة يجب أن تكون ${min} أحرف على الأقل`;
    return null;
  }

  function validateAddress(value) {
    const err = validateRequired(value, 'العنوان');
    if (err) return err;
    if (String(value).trim().length < 5) return 'العنوان قصير جدًا';
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

  function setupAuthForms() {
    bindForm(document.getElementById('loginForm'), (form) => {
      const phone = form.querySelector('#loginPhone');
      const password = form.querySelector('#loginPassword');
      let msg = validatePhone(phone?.value, true);
      if (msg) return fail(phone, msg);
      msg = validateRequired(password?.value, 'كلمة المرور');
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

  document.addEventListener('DOMContentLoaded', setupAuthForms);

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
    normalizePhone,
  };
})(window);
