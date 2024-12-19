from django.urls import path
from django.contrib import admin
from . import views

urlpatterns=[

    path('signup/', views.signup, name='signup'),
     path('admin/', admin.site.urls),  # Admin interface
     path('login/', views.login_user, name='login'),
    path('logout/', views.logout_view, name='logout'),
path('', views.store, name = 'store'),
 path('category/<int:category_id>/', views.store, name='store_by_category'), 
path('products/', views.product_list, name='product_list'),  # Show all products
    path('products/category/<int:category_id>/', views.product_list, name='filter_by_category'),  # Filter by category
path('about/', views.about_us, name='about_us'),  # This defines the URL for the About Us page
path('contact/', views.contact_us, name='contact_us'),
  path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
path('cart/', views.cart, name = 'cart'),
path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
path('checkout/', views.checkout, name = 'checkout'),
path('orders/', views.view_orders, name='view_orders'),  # New path for viewing orders
    path('order/<uuid:order_id>/', views.order_detail, name='order_detail'),  # Detail view for a specific order
    path('order/<uuid:order_id>/payment/', views.process_payment, name='process_payment'),
path('create-customer/', views.create_customer, name='create_customer'),




]