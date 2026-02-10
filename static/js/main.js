/**
 * Smart E-Commerce System - Main JavaScript
 * Custom JavaScript functions and utilities
 */

// ===================================================================
// DOCUMENT READY
// ===================================================================

$(document).ready(function() {
    console.log('Smart E-Commerce System Loaded');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Auto-dismiss alerts
    autoDismissAlerts();
});

// ===================================================================
// UTILITY FUNCTIONS
// ===================================================================

/**
 * Format number as currency (INR)
 */
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

/**
 * Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-IN', options);
}

/**
 * Show loading spinner
 */
function showLoading(buttonElement) {
    const originalText = buttonElement.html();
    buttonElement.data('original-text', originalText);
    buttonElement.html('<span class="spinner-border spinner-border-sm me-2"></span>Loading...');
    buttonElement.prop('disabled', true);
}

/**
 * Hide loading spinner
 */
function hideLoading(buttonElement) {
    const originalText = buttonElement.data('original-text');
    buttonElement.html(originalText);
    buttonElement.prop('disabled', false);
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Append toast to body or toast container
    $('body').append(toast);
    $('.toast').toast('show');
}

/**
 * Confirm action dialog
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// ===================================================================
// INITIALIZATION FUNCTIONS
// ===================================================================

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize form validations
 */
function initializeFormValidations() {
    // Bootstrap validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Auto-dismiss alerts after 5 seconds
 */
function autoDismissAlerts() {
    setTimeout(function() {
        $('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
}

// ===================================================================
// CART FUNCTIONS
// ===================================================================

/**
 * Add to cart with AJAX
 */
function addToCartAjax(productId, quantity = 1) {
    $.ajax({
        url: `/cart/add/${productId}`,
        method: 'POST',
        data: { quantity: quantity },
        success: function(response) {
            showToast('Product added to cart!', 'success');
            updateCartCount();
        },
        error: function(xhr) {
            showToast('Failed to add product to cart.', 'danger');
        }
    });
}

/**
 * Update cart count badge
 */
function updateCartCount() {
    $.ajax({
        url: '/cart/count',
        method: 'GET',
        success: function(response) {
            $('.cart-count').text(response.count);
            if (response.count > 0) {
                $('.cart-count').show();
            } else {
                $('.cart-count').hide();
            }
        }
    });
}

/**
 * Remove from cart with confirmation
 */
function removeFromCart(cartId) {
    confirmAction('Are you sure you want to remove this item?', function() {
        window.location.href = `/cart/remove/${cartId}`;
    });
}

// ===================================================================
// SEARCH FUNCTIONS
// ===================================================================

/**
 * Live search products
 */
function liveSearch(searchTerm) {
    if (searchTerm.length < 3) {
        $('#search-results').hide();
        return;
    }
    
    $.ajax({
        url: '/products/search',
        method: 'GET',
        data: { q: searchTerm },
        success: function(response) {
            displaySearchResults(response.products);
        }
    });
}

/**
 * Display search results
 */
function displaySearchResults(products) {
    const resultsHtml = products.map(product => `
        <a href="/products/${product.id}" class="list-group-item list-group-item-action">
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${product.name}</h6>
                <small>${formatCurrency(product.price)}</small>
            </div>
            <p class="mb-1 text-muted small">${product.category_name}</p>
        </a>
    `).join('');
    
    $('#search-results').html(resultsHtml).show();
}

// ===================================================================
// IMAGE FUNCTIONS
// ===================================================================

/**
 * Handle image load error
 */
function handleImageError(img) {
    img.src = '/static/images/placeholder.jpg';
    img.onerror = null; // Prevent infinite loop
}

/**
 * Lazy load images
 */
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// ===================================================================
// QUANTITY FUNCTIONS
// ===================================================================

/**
 * Increment quantity
 */
function incrementQuantity(inputId) {
    const input = $(`#${inputId}`);
    const currentValue = parseInt(input.val()) || 0;
    const maxValue = parseInt(input.attr('max')) || 999;
    
    if (currentValue < maxValue) {
        input.val(currentValue + 1);
    }
}

/**
 * Decrement quantity
 */
function decrementQuantity(inputId) {
    const input = $(`#${inputId}`);
    const currentValue = parseInt(input.val()) || 0;
    const minValue = parseInt(input.attr('min')) || 1;
    
    if (currentValue > minValue) {
        input.val(currentValue - 1);
    }
}

// ===================================================================
// VALIDATION FUNCTIONS
// ===================================================================

/**
 * Validate email format
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate phone number (10 digits)
 */
function validatePhone(phone) {
    const re = /^[0-9]{10}$/;
    return re.test(phone);
}

/**
 * Validate PIN code (6 digits)
 */
function validatePincode(pincode) {
    const re = /^[0-9]{6}$/;
    return re.test(pincode);
}

/**
 * Check password strength
 */
function checkPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 6) strength++;
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
    if (password.match(/\d/)) strength++;
    if (password.match(/[^a-zA-Z\d]/)) strength++;
    
    return strength; // 0: weak, 1-2: medium, 3-4: strong
}

// ===================================================================
// ADMIN FUNCTIONS
// ===================================================================

/**
 * Confirm delete action
 */
function confirmDelete(itemName, deleteUrl) {
    if (confirm(`Are you sure you want to delete ${itemName}?`)) {
        window.location.href = deleteUrl;
    }
}

/**
 * Toggle user status
 */
function toggleUserStatus(userId) {
    confirmAction('Are you sure you want to change this user\'s status?', function() {
        window.location.href = `/admin/user/toggle-status/${userId}`;
    });
}

// ===================================================================
// FILTER FUNCTIONS
// ===================================================================

/**
 * Apply price filter
 */
function applyPriceFilter() {
    const minPrice = $('#min-price').val();
    const maxPrice = $('#max-price').val();
    const currentUrl = new URL(window.location.href);
    
    if (minPrice) currentUrl.searchParams.set('min_price', minPrice);
    if (maxPrice) currentUrl.searchParams.set('max_price', maxPrice);
    
    window.location.href = currentUrl.toString();
}

/**
 * Clear all filters
 */
function clearFilters() {
    window.location.href = window.location.pathname;
}

// ===================================================================
// SMOOTH SCROLL
// ===================================================================

/**
 * Smooth scroll to element
 */
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// ===================================================================
// LOCAL STORAGE FUNCTIONS
// ===================================================================

/**
 * Save to local storage
 */
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (e) {
        console.error('Error saving to localStorage:', e);
        return false;
    }
}

/**
 * Get from local storage
 */
function getFromLocalStorage(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (e) {
        console.error('Error reading from localStorage:', e);
        return null;
    }
}

// ===================================================================
// EXPORT FUNCTIONS
// ===================================================================

/**
 * Export table to CSV
 */
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    const rows = Array.from(table.querySelectorAll('tr'));
    
    const csv = rows.map(row => {
        const cells = Array.from(row.querySelectorAll('td, th'));
        return cells.map(cell => `"${cell.textContent.trim()}"`).join(',');
    }).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// ===================================================================
// PRINT FUNCTIONS
// ===================================================================

/**
 * Print page section
 */
function printSection(sectionId) {
    const section = document.getElementById(sectionId);
    const printWindow = window.open('', '', 'height=600,width=800');
    
    printWindow.document.write('<html><head><title>Print</title>');
    printWindow.document.write('<link rel="stylesheet" href="/static/css/style.css">');
    printWindow.document.write('</head><body>');
    printWindow.document.write(section.innerHTML);
    printWindow.document.write('</body></html>');
    
    printWindow.document.close();
    printWindow.print();
}

// ===================================================================
// EVENT LISTENERS
// ===================================================================

// Search input with debounce
let searchTimeout;
$('#search-input').on('input', function() {
    clearTimeout(searchTimeout);
    const searchTerm = $(this).val();
    searchTimeout = setTimeout(() => liveSearch(searchTerm), 300);
});

// Close search results when clicking outside
$(document).on('click', function(e) {
    if (!$(e.target).closest('#search-container').length) {
        $('#search-results').hide();
    }
});

// Back to top button
$(window).scroll(function() {
    if ($(this).scrollTop() > 200) {
        $('#back-to-top').fadeIn();
    } else {
        $('#back-to-top').fadeOut();
    }
});

$('#back-to-top').click(function() {
    $('html, body').animate({ scrollTop: 0 }, 800);
    return false;
});


// ===================================================================
// AUTOCOMPLETE SEARCH
// ===================================================================

$(document).ready(function() {
    const searchInput = $('#searchInput');
    const searchSuggestions = $('#searchSuggestions');
    let debounceTimer;

    // Listen for input
    searchInput.on('input', function() {
        clearTimeout(debounceTimer);
        const query = $(this).val().trim();

        if (query.length < 2) {
            searchSuggestions.hide();
            return;
        }

        debounceTimer = setTimeout(() => {
            fetchSuggestions(query);
        }, 300);
    });

    // Fetch suggestions from API
    function fetchSuggestions(query) {
        $.ajax({
            url: '/products/search/suggestions',
            method: 'GET',
            data: { q: query },
            success: function(response) {
                renderSuggestions(response);
            },
            error: function() {
                searchSuggestions.hide();
            }
        });
    }

    // Render suggestions
    function renderSuggestions(products) {
        if (!products || products.length === 0) {
            searchSuggestions.hide();
            return;
        }

        const html = products.map(product => `
            <a href="/products/${product.id}" class="suggestion-item d-flex align-items-center p-2 text-decoration-none border-bottom">
                <img src="${product.image_url || '/static/images/placeholder.jpg'}" alt="${product.name}" class="rounded me-3" style="width: 40px; height: 40px; object-fit: cover;">
                <div class="flex-grow-1">
                    <div class="text-dark fw-bold small">${product.name}</div>
                    <div class="text-muted" style="font-size: 0.8rem;">₹${parseFloat(product.price).toFixed(2)}</div>
                </div>
            </a>
        `).join('');

        searchSuggestions.html(html).show();
    }

    // Hide suggestions when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.search-form').length) {
            searchSuggestions.hide();
        }
    });
    
    // Show suggestions again if input has value and is focused
    searchInput.on('focus', function() {
        if ($(this).val().trim().length >= 2) {
            // Re-fetch or just show if we cached? For now re-fetch is safer
            fetchSuggestions($(this).val().trim());
        }
    });
});

console.log('All JavaScript functions loaded successfully!');