/* Entity Medical - Profile Logic
   Handles dynamic data population for profile.html
*/

(function () {
    'use strict';

    // Simulated User Data (In a real app, this would come from an API/Backend)
    const user = {
        name: "د. عمر الشريف",
        phone: "01013928114",
        email: "omar@entity-medical.com",
        joinedDate: "يناير 2024",
        stats: {
            orders: 5,
            favorites: 12,
            points: 1540
        }
    };

    function initProfile() {
        // 1. Populate Header & Card
        const pNameHeader = document.getElementById('pNameHeader');
        const pNameCard = document.getElementById('pNameCard');
        const pPhoneCard = document.getElementById('pPhoneCard');
        const pCreatedCard = document.getElementById('pCreatedCard');

        if (pNameHeader) pNameHeader.textContent = user.name;
        if (pNameCard) pNameCard.textContent = user.name;
        if (pPhoneCard) pPhoneCard.textContent = user.phone;
        if (pCreatedCard) pCreatedCard.textContent = user.joinedDate;

        // 2. Populate Stats
        const statOrders = document.getElementById('statOrders');
        const statFavs = document.getElementById('statFavs');
        const statPoints = document.getElementById('statPoints');

        if (statOrders) statOrders.textContent = user.stats.orders;
        if (statFavs) statFavs.textContent = user.stats.favorites;
        if (statPoints) statPoints.textContent = user.stats.points;

        // 3. Populate Form Fields
        const profileName = document.getElementById('profileName');
        const profilePhone = document.getElementById('profilePhone');
        const profileEmail = document.getElementById('profileEmail');

        if (profileName) profileName.value = user.name;
        if (profilePhone) profilePhone.value = user.phone;
        if (profileEmail) profileEmail.value = user.email;

        // 4. Handle Logout
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                const confirmLogout = confirm('هل أنت متأكد من تسجيل الخروج؟');
                if (confirmLogout) {
                    localStorage.removeItem('currentUser');
                    window.location.href = 'login.html';
                }
            });
        }

        // 5. Handle Form Submission
        const profileForm = document.getElementById('profileForm');
        if (profileForm) {
            profileForm.addEventListener('submit', (e) => {
                e.preventDefault();
                // Simulate saving
                const btn = profileForm.querySelector('button[type="submit"]');
                const originalText = btn.textContent;
                btn.textContent = 'جاري الحفظ...';
                btn.disabled = true;

                setTimeout(() => {
                    btn.textContent = 'تم الحفظ ✔';
                    setTimeout(() => {
                        btn.textContent = originalText;
                        btn.disabled = false;
                        // Update UI with new values if needed
                        user.name = profileName.value;
                        if (pNameHeader) pNameHeader.textContent = user.name;
                        if (pNameCard) pNameCard.textContent = user.name;
                    }, 1500);
                }, 1000);
            });
        }
    }

    document.addEventListener('DOMContentLoaded', initProfile);

})();
