"""
Analytics Routes
Handles analytics dashboard and reporting
"""

from flask import Blueprint, render_template, jsonify, request
from models.analytics import Analytics
from utils.decorators import admin_required

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/dashboard')
@admin_required
def dashboard():
    """Analytics dashboard with charts"""
    # Get dashboard statistics
    stats = Analytics.get_dashboard_stats()
    
    # Get daily sales (last 30 days)
    daily_sales = Analytics.get_daily_sales(days=30)
    
    # Get best-selling products
    best_products = Analytics.get_best_selling_products(limit=10)
    
    # Get category-wise sales
    category_sales = Analytics.get_category_wise_sales()
    
    # Get payment method statistics
    payment_stats = Analytics.get_payment_method_stats()
    
    return render_template('admin/analytics.html',
                         stats=stats,
                         daily_sales=daily_sales,
                         best_products=best_products,
                         category_sales=category_sales,
                         payment_stats=payment_stats)


@analytics_bp.route('/sales-data')
@admin_required
def sales_data():
    """Get sales data for charts (JSON API)"""
    days = request.args.get('days', 30, type=int)
    daily_sales = Analytics.get_daily_sales(days=days)
    
    # Format data for Chart.js
    data = {
        'labels': [str(item['sale_date']) for item in daily_sales],
        'datasets': [{
            'label': 'Revenue',
            'data': [float(item['revenue']) for item in daily_sales],
            'borderColor': 'rgb(54, 162, 235)',
            'backgroundColor': 'rgba(54, 162, 235, 0.1)'
        }, {
            'label': 'Order Count',
            'data': [int(item['order_count']) for item in daily_sales],
            'borderColor': 'rgb(75, 192, 192)',
            'backgroundColor': 'rgba(75, 192, 192, 0.1)'
        }]
    }
    
    return jsonify(data)


@analytics_bp.route('/category-data')
@admin_required
def category_data():
    """Get category sales data (JSON API)"""
    category_sales = Analytics.get_category_wise_sales()
    
    data = {
        'labels': [item['category_name'] for item in category_sales],
        'datasets': [{
            'label': 'Revenue by Category',
            'data': [float(item['revenue']) for item in category_sales],
            'backgroundColor': [
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(153, 102, 255, 0.7)',
                'rgba(255, 159, 64, 0.7)'
            ]
        }]
    }
    
    return jsonify(data)


@analytics_bp.route('/payment-data')
@admin_required
def payment_data():
    """Get payment method data (JSON API)"""
    payment_stats = Analytics.get_payment_method_stats()
    
    data = {
        'labels': [item['payment_method'] for item in payment_stats],
        'datasets': [{
            'label': 'Transactions by Payment Method',
            'data': [int(item['transaction_count']) for item in payment_stats],
            'backgroundColor': [
                'rgba(255, 99, 132, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(255, 206, 86, 0.8)'
            ]
        }]
    }
    
    return jsonify(data)