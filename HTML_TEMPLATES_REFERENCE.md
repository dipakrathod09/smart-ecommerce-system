# HTML TEMPLATES REFERENCE
# All templates for Smart E-Commerce System
# These are sample templates demonstrating the structure

## BASE TEMPLATE (templates/base.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Smart E-Commerce{% endblock %}</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fas fa-shopping-cart"></i> Smart E-Commerce
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('index') }}">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('product.list_products') }}">Products</a>
                    </li>
                    {% if user_info.logged_in %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('user.dashboard') }}">Dashboard</a>
                    </li>
                    {% endif %}
                </ul>
                
                <ul class="navbar-nav">
                    {% if user_info.logged_in %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('cart.view_cart') }}">
                                <i class="fas fa-shopping-cart"></i> Cart 
                                {% if cart_count > 0 %}
                                <span class="badge bg-danger">{{ cart_count }}</span>
                                {% endif %}
                            </a>
                        </li>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" 
                               data-bs-toggle="dropdown">
                                <i class="fas fa-user"></i> {{ user_info.user_name }}
                            </a>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="{{ url_for('user.profile') }}">Profile</a></li>
                                <li><a class="dropdown-item" href="{{ url_for('order.order_history') }}">Orders</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="{{ url_for('auth.logout') }}">Logout</a></li>
                            </ul>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.login') }}">
                                <i class="fas fa-sign-in-alt"></i> Login
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.register') }}">
                                <i class="fas fa-user-plus"></i> Register
                            </a>
                        </li>
                    {% endif %}
                    
                    {% if user_info.is_admin %}
                        <li class="nav-item">
                            <a class="nav-link btn btn-warning btn-sm ms-2" 
                               href="{{ url_for('admin.dashboard') }}">
                                <i class="fas fa-cog"></i> Admin Panel
                            </a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    <div class="container mt-3">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    <!-- Main Content -->
    <main class="container my-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="bg-dark text-white mt-5 py-4">
        <div class="container text-center">
            <p>&copy; 2026 Smart E-Commerce System. Final Year BE Project.</p>
            <p>Technology Stack: Flask, PostgreSQL, Bootstrap</p>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    
    <!-- Custom JS -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

## HOME PAGE (templates/index.html)

```html
{% extends 'base.html' %}

{% block title %}Home - Smart E-Commerce{% endblock %}

{% block content %}
<div class="jumbotron bg-light p-5 rounded">
    <h1 class="display-4">Welcome to Smart E-Commerce!</h1>
    <p class="lead">Shop the latest products with our intelligent recommendation system.</p>
    <hr class="my-4">
    <p>Browse our extensive catalog and enjoy seamless shopping experience.</p>
    <a class="btn btn-primary btn-lg" href="{{ url_for('product.list_products') }}" role="button">
        <i class="fas fa-shopping-bag"></i> Start Shopping
    </a>
</div>

<!-- Categories Section -->
<section class="my-5">
    <h2 class="mb-4">Shop by Category</h2>
    <div class="row">
        {% for category in categories %}
        <div class="col-md-3 mb-3">
            <div class="card h-100 text-center">
                <div class="card-body">
                    <i class="fas fa-box fa-3x mb-3 text-primary"></i>
                    <h5 class="card-title">{{ category.name }}</h5>
                    <a href="{{ url_for('product.list_products', category=category.id) }}" 
                       class="btn btn-sm btn-outline-primary">Browse</a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</section>

<!-- Featured Products -->
<section class="my-5">
    <h2 class="mb-4">Featured Products</h2>
    <div class="row">
        {% for product in featured_products %}
        <div class="col-md-3 mb-4">
            <div class="card h-100">
                <img src="{{ product.image_url or '/static/images/placeholder.jpg' }}" 
                     class="card-img-top" alt="{{ product.name }}" style="height: 200px; object-fit: cover;">
                <div class="card-body">
                    <h5 class="card-title">{{ product.name }}</h5>
                    <p class="text-muted">{{ product.category_name }}</p>
                    <h4 class="text-primary">{{ product.price|currency }}</h4>
                    <a href="{{ url_for('product.product_detail', product_id=product.id) }}" 
                       class="btn btn-primary btn-sm w-100">View Details</a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</section>
{% endblock %}
```

## LOGIN PAGE (templates/auth/login.html)

```html
{% extends 'base.html' %}

{% block title %}Login - Smart E-Commerce{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card shadow">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0"><i class="fas fa-sign-in-alt"></i> User Login</h4>
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('auth.login') }}">
                    <div class="mb-3">
                        <label for="email" class="form-label">Email Address</label>
                        <input type="email" class="form-control" id="email" name="email" 
                               placeholder="Enter your email" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" 
                               placeholder="Enter your password" required>
                    </div>
                    
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="fas fa-sign-in-alt"></i> Login
                    </button>
                </form>
                
                <hr>
                
                <p class="text-center mb-0">
                    Don't have an account? 
                    <a href="{{ url_for('auth.register') }}">Register here</a>
                </p>
                
                <p class="text-center mt-2">
                    <a href="{{ url_for('auth.admin_login') }}" class="text-muted">
                        <i class="fas fa-user-shield"></i> Admin Login
                    </a>
                </p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## PRODUCT LISTING (templates/user/products.html)

```html
{% extends 'base.html' %}

{% block title %}Products - Smart E-Commerce{% endblock %}

{% block content %}
<h1 class="mb-4">Our Products</h1>

<!-- Filters and Search -->
<div class="row mb-4">
    <div class="col-md-3">
        <h5>Categories</h5>
        <div class="list-group">
            <a href="{{ url_for('product.list_products') }}" 
               class="list-group-item list-group-item-action {% if not selected_category %}active{% endif %}">
                All Products
            </a>
            {% for category in categories %}
            <a href="{{ url_for('product.list_products', category=category.id) }}" 
               class="list-group-item list-group-item-action {% if selected_category == category.id %}active{% endif %}">
                {{ category.name }}
            </a>
            {% endfor %}
        </div>
    </div>
    
    <div class="col-md-9">
        <!-- Search Bar -->
        <form method="GET" class="mb-3">
            <div class="input-group">
                <input type="text" class="form-control" name="search" 
                       placeholder="Search products..." value="{{ search_term }}">
                <button class="btn btn-primary" type="submit">
                    <i class="fas fa-search"></i> Search
                </button>
            </div>
        </form>
        
        <!-- Products Grid -->
        <div class="row">
            {% if products %}
                {% for product in products %}
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <img src="{{ product.image_url or '/static/images/placeholder.jpg' }}" 
                             class="card-img-top" alt="{{ product.name }}" 
                             style="height: 200px; object-fit: cover;">
                        <div class="card-body">
                            <h5 class="card-title">{{ product.name }}</h5>
                            <p class="text-muted small">{{ product.category_name }}</p>
                            <p class="card-text">{{ product.description[:80] }}...</p>
                            <h4 class="text-primary">{{ product.price|currency }}</h4>
                            
                            {% if product.stock > 0 %}
                                <span class="badge bg-success">In Stock: {{ product.stock }}</span>
                            {% else %}
                                <span class="badge bg-danger">Out of Stock</span>
                            {% endif %}
                        </div>
                        <div class="card-footer">
                            <a href="{{ url_for('product.product_detail', product_id=product.id) }}" 
                               class="btn btn-primary btn-sm w-100">View Details</a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="col-12">
                    <div class="alert alert-info">
                        No products found. Try different search criteria.
                    </div>
                </div>
            {% endif %}
        </div>
        
        <!-- Pagination -->
        {% if total_pages > 1 %}
        <nav>
            <ul class="pagination justify-content-center">
                {% for page_num in range(1, total_pages + 1) %}
                <li class="page-item {% if page_num == current_page %}active{% endif %}">
                    <a class="page-link" href="{{ url_for('product.list_products', page=page_num, category=selected_category, search=search_term) }}">
                        {{ page_num }}
                    </a>
                </li>
                {% endfor %}
            </ul>
        </nav>
        {% endif %}
    </div>
</div>
{% endblock %}
```

## SHOPPING CART (templates/user/cart.html)

```html
{% extends 'base.html' %}

{% block title %}Shopping Cart - Smart E-Commerce{% endblock %}

{% block content %}
<h1 class="mb-4"><i class="fas fa-shopping-cart"></i> Shopping Cart</h1>

{% if cart_items %}
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Price</th>
                            <th>Quantity</th>
                            <th>Subtotal</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in cart_items %}
                        <tr>
                            <td>
                                <div class="d-flex align-items-center">
                                    <img src="{{ item.image_url or '/static/images/placeholder.jpg' }}" 
                                         width="80" class="me-3">
                                    <div>
                                        <h6 class="mb-0">{{ item.name }}</h6>
                                        <small class="text-muted">{{ item.brand }}</small>
                                    </div>
                                </div>
                            </td>
                            <td>{{ item.price|currency }}</td>
                            <td>
                                <form method="POST" action="{{ url_for('cart.update_cart', cart_id=item.cart_id) }}" 
                                      class="d-inline">
                                    <input type="number" name="quantity" value="{{ item.quantity }}" 
                                           min="1" max="{{ item.stock }}" class="form-control form-control-sm" 
                                           style="width: 80px;" onchange="this.form.submit()">
                                </form>
                            </td>
                            <td><strong>{{ item.subtotal|currency }}</strong></td>
                            <td>
                                <a href="{{ url_for('cart.remove_from_cart', cart_id=item.cart_id) }}" 
                                   class="btn btn-sm btn-danger" 
                                   onclick="return confirm('Remove this item?')">
                                    <i class="fas fa-trash"></i>
                                </a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Order Summary</h5>
            </div>
            <div class="card-body">
                <div class="d-flex justify-content-between mb-2">
                    <span>Subtotal:</span>
                    <strong>{{ cart_total|currency }}</strong>
                </div>
                <div class="d-flex justify-content-between mb-2">
                    <span>Shipping:</span>
                    <strong>FREE</strong>
                </div>
                <hr>
                <div class="d-flex justify-content-between mb-3">
                    <h5>Total:</h5>
                    <h5 class="text-primary">{{ cart_total|currency }}</h5>
                </div>
                
                <a href="{{ url_for('order.checkout') }}" class="btn btn-success w-100 mb-2">
                    <i class="fas fa-credit-card"></i> Proceed to Checkout
                </a>
                <a href="{{ url_for('product.list_products') }}" class="btn btn-outline-primary w-100">
                    <i class="fas fa-shopping-bag"></i> Continue Shopping
                </a>
            </div>
        </div>
    </div>
</div>
{% else %}
<div class="alert alert-info">
    <h4><i class="fas fa-info-circle"></i> Your cart is empty!</h4>
    <p>Browse our products and add items to your cart.</p>
    <a href="{{ url_for('product.list_products') }}" class="btn btn-primary">
        <i class="fas fa-shopping-bag"></i> Start Shopping
    </a>
</div>
{% endif %}
{% endblock %}
```

## ADMIN DASHBOARD (templates/admin/dashboard.html)

```html
{% extends 'base.html' %}

{% block title %}Admin Dashboard - Smart E-Commerce{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/admin.css') }}">
{% endblock %}

{% block content %}
<h1 class="mb-4"><i class="fas fa-tachometer-alt"></i> Admin Dashboard</h1>

<!-- Statistics Cards -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card bg-primary text-white">
            <div class="card-body">
                <h6 class="text-uppercase">Total Revenue</h6>
                <h2>{{ stats.total_revenue|currency }}</h2>
                <i class="fas fa-rupee-sign fa-3x opacity-50"></i>
            </div>
        </div>
    </div>
    
    <div class="col-md-3">
        <div class="card bg-success text-white">
            <div class="card-body">
                <h6 class="text-uppercase">Total Orders</h6>
                <h2>{{ stats.total_orders }}</h2>
                <i class="fas fa-shopping-cart fa-3x opacity-50"></i>
            </div>
        </div>
    </div>
    
    <div class="col-md-3">
        <div class="card bg-info text-white">
            <div class="card-body">
                <h6 class="text-uppercase">Total Users</h6>
                <h2>{{ stats.total_users }}</h2>
                <i class="fas fa-users fa-3x opacity-50"></i>
            </div>
        </div>
    </div>
    
    <div class="col-md-3">
        <div class="card bg-warning text-white">
            <div class="card-body">
                <h6 class="text-uppercase">Low Stock Items</h6>
                <h2>{{ stats.low_stock_count }}</h2>
                <i class="fas fa-exclamation-triangle fa-3x opacity-50"></i>
            </div>
        </div>
    </div>
</div>

<!-- Quick Actions -->
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5>Quick Actions</h5>
            </div>
            <div class="card-body">
                <a href="{{ url_for('admin.manage_products') }}" class="btn btn-primary me-2">
                    <i class="fas fa-box"></i> Manage Products
                </a>
                <a href="{{ url_for('admin.manage_categories') }}" class="btn btn-info me-2">
                    <i class="fas fa-tags"></i> Manage Categories
                </a>
                <a href="{{ url_for('admin.manage_orders') }}" class="btn btn-success me-2">
                    <i class="fas fa-shopping-cart"></i> Manage Orders
                </a>
                <a href="{{ url_for('analytics.dashboard') }}" class="btn btn-warning">
                    <i class="fas fa-chart-bar"></i> View Analytics
                </a>
            </div>
        </div>
    </div>
</div>

<!-- Recent Orders -->
<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5>Recent Orders</h5>
            </div>
            <div class="card-body">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Order #</th>
                            <th>Customer</th>
                            <th>Amount</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for order in recent_orders %}
                        <tr>
                            <td>{{ order.order_number }}</td>
                            <td>{{ order.customer_name }}</td>
                            <td>{{ order.total_amount|currency }}</td>
                            <td><span class="badge bg-info">{{ order.order_status }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-danger text-white">
                <h5 class="mb-0">Low Stock Alerts</h5>
            </div>
            <div class="card-body">
                {% if low_stock %}
                <ul class="list-group">
                    {% for product in low_stock %}
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        {{ product.name }}
                        <span class="badge bg-danger">Stock: {{ product.stock }}</span>
                    </li>
                    {% endfor %}
                </ul>
                {% else %}
                <p class="text-success">All products have sufficient stock!</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Additional Templates Note

The following templates follow similar patterns:
- templates/auth/register.html
- templates/user/checkout.html
- templates/user/order_history.html
- templates/user/order_detail.html
- templates/admin/categories.html
- templates/admin/products.html
- templates/admin/orders.html
- templates/admin/analytics.html (with Chart.js integration)
- templates/payment/select_method.html
- templates/payment/success.html

All templates use Bootstrap 5 for responsive design and follow the same structure with the base template.
