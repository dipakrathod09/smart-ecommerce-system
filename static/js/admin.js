// Admin Panel Scripts

document.addEventListener('DOMContentLoaded', function () {
    // Confirmation Dialog for Delete Actions
    const deleteForms = document.querySelectorAll('form[data-confirm]');

    deleteForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const message = this.dataset.confirm || 'Are you sure you want to proceed?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});
