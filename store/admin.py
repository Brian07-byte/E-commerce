from django.contrib import admin
from .models import (
    Customer, Category, Product, NewProduct, FlashSaleProduct, Cart, 
    CartItem, ShippingAdress, Order, Payment, Testimonial
)

# Register Customer Model
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email')
    search_fields = ('name', 'email')

admin.site.register(Customer, CustomerAdmin)

# Register Category Model
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

admin.site.register(Category, CategoryAdmin)

# Register Product Model
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'old_price', 'new_price', 'category', 'flash_sale', 'flash_sale_start_time', 'flash_sale_end_time', 'image')
    list_filter = ('flash_sale', 'category')
    search_fields = ('name',)
    list_editable = ('price', 'flash_sale')

    def flash_sale_status(self, obj):
        return "Active" if obj.flash_sale else "Inactive"
    flash_sale_status.short_description = 'Flash Sale Status'

admin.site.register(Product, ProductAdmin)

# Register NewProduct Model
class NewProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_new', 'price', 'image')
    search_fields = ('product__name',)

admin.site.register(NewProduct, NewProductAdmin)

# Register FlashSaleProduct Model
class FlashSaleProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'flash_sale_start_time', 'flash_sale_end_time', 'get_flash_sale_countdown', 'image')
    list_filter = ('flash_sale_start_time', 'flash_sale_end_time')
    search_fields = ('product__name',)

    def get_flash_sale_countdown(self, obj):
        return obj.get_flash_sale_countdown()
    get_flash_sale_countdown.short_description = 'Time Remaining'

admin.site.register(FlashSaleProduct, FlashSaleProductAdmin)

# Register Cart Model
class CartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'cart_id', 'completed')
    list_filter = ('completed',)
    search_fields = ('cart_id',)

admin.site.register(Cart, CartAdmin)

# Register CartItem Model
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('product__name',)
    list_filter = ('cart',)

admin.site.register(CartItem, CartItemAdmin)

# Register Shipping Address Model
class ShippingAdressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'cart', 'adress', 'city', 'state', 'zipcode')
    search_fields = ('customer__name', 'adress', 'city')

admin.site.register(ShippingAdress, ShippingAdressAdmin)

# Register Order Model
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'created_at', 'total_amount', 'is_paid')
    list_filter = ('is_paid',)
    search_fields = ('order_id', 'customer__name')

admin.site.register(Order, OrderAdmin)

# Register Payment Model
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'payment_date', 'payment_method', 'payment_amount', 'payment_status')
    list_filter = ('payment_status', 'payment_method')
    search_fields = ('order__order_id', 'user__username')

admin.site.register(Payment, PaymentAdmin)

# Register Testimonial Model
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'created_at', 'image')
    search_fields = ('customer_name',)
    list_filter = ('created_at',)

admin.site.register(Testimonial, TestimonialAdmin)
