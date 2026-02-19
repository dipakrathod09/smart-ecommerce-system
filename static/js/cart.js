// Cart Operations

document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for quantity buttons if they exist
    const quantityInputs = document.querySelectorAll('.quantity-input');
    
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const cartId = this.dataset.cartId;
            const quantity = this.value;
            updateCart(cartId, quantity);
        });
    });
});

function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

function showToast(message, type = 'success') {
    // Create a simple toast or alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show fixed-top m-3`;
    alertDiv.style.zIndex = '1050';
    alertDiv.innerHTML = `
        <strong>${type === 'success' ? 'Success!' : 'Error!'}</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    // Auto dismiss
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

function updateCart(cartId, quantity) {
    if (quantity < 1) return;

    fetch(`/cart/update/${cartId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ quantity: parseInt(quantity) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update UI
            // Update Item Subtotal
            const subtotalElement = document.querySelector(`#subtotal-${cartId}`);
            if (subtotalElement) {
                subtotalElement.textContent = '₹' + parseFloat(data.item_subtotal).toFixed(2);
            }
            
            // Update Cart Total
            const totalElement = document.querySelector('#cart-total');
            if (totalElement) {
                totalElement.textContent = '₹' + parseFloat(data.cart_total).toFixed(2);
            }
            
            // Update Cart Badge
            const badgeElement = document.querySelector('.fa-shopping-bag + .badge');
            if (badgeElement) {
                if (data.cart_count > 0) {
                    badgeElement.textContent = data.cart_count;
                    badgeElement.style.display = 'inline-block';
                } else {
                    badgeElement.style.display = 'none';
                }
            }
            
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'danger');
    });
}

function removeFromCart(cartId) {
    if (!confirm('Are you sure you want to remove this item?')) return;

    fetch(`/cart/remove/${cartId}`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove row
            const row = document.querySelector(`#row-${cartId}`);
            if (row) row.remove();
            
            // Update Cart Total
            const totalElement = document.querySelector('#cart-total');
            if (totalElement) {
                totalElement.textContent = '₹' + parseFloat(data.cart_total).toFixed(2);
            }
            
            // Update Cart Badge
            const badgeElement = document.querySelector('.fa-shopping-bag + .badge');
            if (badgeElement) {
                badgeElement.textContent = data.cart_count;
                if (data.cart_count === 0) badgeElement.style.display = 'none';
            }
            
            // Check if cart is empty
            if (data.cart_count === 0) {
                location.reload(); // Reload to show empty cart message
            }
            
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred.', 'danger');
    });
}
