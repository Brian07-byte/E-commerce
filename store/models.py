from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta

# Existing Customer Model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)

    def __str__(self):
        return self.name

# Existing Category Model
class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

# Updated Product Model with added flash sale start and end times
class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()  # New price
    old_price = models.IntegerField(null=True, blank=True)  # Old price (if available)
    new_price = models.IntegerField(null=True, blank=True)  # New price (optional)
    image = models.ImageField(upload_to='products/')
    flash_sale = models.BooleanField(default=False)  # Flash sale indicator
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)  # Link to category

    # For Flash Sale countdown
    flash_sale_start_time = models.DateTimeField(null=True, blank=True)  # Start time of flash sale
    flash_sale_end_time = models.DateTimeField(null=True, blank=True)  # End time of flash sale

    def __str__(self):
        return self.name

    def get_flash_sale_countdown(self):
        """
        Returns the countdown in seconds if the flash sale is active.
        """
        from django.utils import timezone

        if self.flash_sale and self.flash_sale_start_time and self.flash_sale_end_time:
            now = timezone.now()
            if now < self.flash_sale_end_time:
                countdown_time = self.flash_sale_end_time - now
                return countdown_time.total_seconds()
        return 0

# New Product Model with Price and Image
class NewProduct(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='new_product')
    is_new = models.BooleanField(default=True)
    price = models.IntegerField()  # New price specific to the new product
    image = models.ImageField(upload_to='new_products/')  # Image specific to the new product

    def __str__(self):
        return f"New product: {self.product.name}"

# Flash Sale Product Model with Price and Image
class FlashSaleProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    flash_sale_start_time = models.DateTimeField()
    flash_sale_end_time = models.DateTimeField()
    image = models.ImageField(upload_to='flash_sales/')
    
    def get_flash_sale_countdown(self):
        """
        Calculate the remaining time for the flash sale.
        Returns a human-readable time format (e.g., hours, minutes).
        """
        remaining_time = self.flash_sale_end_time - timezone.now()
        if remaining_time < timedelta(seconds=0):
            return "Flash Sale Ended"
        else:
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{remaining_time.days}d {hours}h {minutes}m {seconds}s"

    def __str__(self):
        return f"Flash Sale Product: {self.product.name}"

# Cart Model
class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cart_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart {self.cart_id} for {self.customer}"

# CartItem Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

# Shipping Address Model
class ShippingAdress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    adress = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)

    def __str__(self):
        return self.adress

# Order Model
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    items = models.ManyToManyField('CartItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.order_id} by {self.customer.name}"

# Payment Model
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=100)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')

    def __str__(self):
        return f'Payment for Order #{self.order.order_id}'

# Testimonial Model
class Testimonial(models.Model):
    customer_name = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)

    def __str__(self):
        return f"Testimonial by {self.customer_name}"
