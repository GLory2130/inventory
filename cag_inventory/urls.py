from django.urls import path
from . import views
from .views import product_list_create_view,product_detail_view, products_in_stock_view,sales_analytics_view,most_consumed_products_view

urlpatterns = [
    path('', views.home, name='home'),
    path('base/',views.base, name="base"),
    path('index/',views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('products/', views.product_list, name='product_list'),
    path('add_product_form/', views.add_product, name='add_product_form'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),
    path('update-stock/<int:pk>/', views.stock_update, name='update-stock'),
    path('update-product/', views.update_product, name='update_product'),
    path('', product_list_create_view, name='product-list-create'),
    path('<int:pk>/', product_detail_view, name='product-detail'),
    path('in-stock/', products_in_stock_view, name='products-in-stock'),
    path('analytics/sales/', sales_analytics_view, name='sales-analytics'),
    path('analytics/most-consumed/', most_consumed_products_view, name='most-consumed-products'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('api/real-time-analytics/', views.real_time_analytics, name='real-time-analytics'),
    path('api/real-time-stats/', views.real_time_stats, name='real_time_stats'),
    path('products/<int:pk>/delete/', views.product_delete_view, name='delete_product'),

]