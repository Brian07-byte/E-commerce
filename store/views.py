from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.contrib import messages
import json
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import ShippingAddressForm
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your views here.
@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_customer(sender, instance, **kwargs):
    instance.customer.save()


def about_us(request):
    products = Product.objects.all()  # Fetch products for the carousel
    testimonials = Testimonial.objects.all()  # Fetch testimonials
    return render(request, 'about_us.html', {'products': products, 'testimonials': testimonials})
def contact_us(request):
    return render(request, 'contact_us.html')
# View to display products by category
def product_list(request, category_id=None):
    categories = Category.objects.all()  # Get all categories
    if category_id:
        # Filter products by category if category_id is provided
        products = Product.objects.filter(category__id=category_id)
    else:
        # If no category is selected, show all products
        products = Product.objects.all()

    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories
    })


def signup(request):
    """View for user signup."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'signup_login.html')

        # Create a new user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Signup successful! Please log in.")
        return redirect('login')  # Redirect to login page after signup

    return render(request, 'signup_login.html')

def login_user(request):
    """View for user login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('store')  # Redirect to a home page or dashboard
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'signup_login.html')

    return render(request, 'signup_login.html')

@login_required
def logout_view(request):
    """View for logging out the user."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('store')

def store(request, category_id=None):
    customer = None
    cart_count = 0
    
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Ensure the user has a related customer
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            # Create a customer if one doesn't exist
            customer = Customer.objects.create(user=request.user)
        
        # Fetch the cart for the authenticated user
        cart = Cart.objects.filter(customer=customer, completed=False).first()
        if cart:
            cart_count = cart.items.count()

    # Fetch all categories
    categories = Category.objects.all()

    # Fetch products, filtered by category if a category_id is provided
    if category_id:
        # Get the category or return a 404 error if it doesn't exist
        selected_category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(category=selected_category)
    else:
        # Fetch all products if no category filter is applied
        products = Product.objects.all()

    # Fetch all flash sale products
    flash_sale_products = FlashSaleProduct.objects.all()

    # Fetch all new products
    new_products = NewProduct.objects.all()

    # Render the page with products, cart count, available categories, flash sale products, and new products
    return render(request, 'store.html', {
        'products': products,
        'cart_count': cart_count,
        'categories': categories,
        'selected_category': selected_category if category_id else None,
        'flash_sale_products': flash_sale_products,
        'new_products': new_products,
    })

@login_required
def cart(request):
    # Ensure the user has a customer object
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        # Create a new customer if one doesn't exist
        customer = Customer(user=request.user)
        customer.save()

    # Get or create the cart for this customer (completed = False means an active cart)
    cart, created = Cart.objects.get_or_create(customer=customer, completed=False)

    # Get all cart items for the current cart using the related_name 'items'
    cart_items = cart.items.all()

    # Handle updating the quantity of items in the cart
    if request.method == "POST":
        for item in cart_items:
            # Get the new quantity from the POST data
            quantity = request.POST.get(f'quantity_{item.id}')
            if quantity:
                item.quantity = int(quantity)
                item.save()

        # After updating, redirect to refresh the page
        return redirect('cart')

    # Calculate the total price for the cart
    cart_total = sum(item.product.price * item.quantity for item in cart_items)

    # Prepare the cart items with their totals to be passed to the template
    cart_items_with_totals = [
        {
            'item': item,
            'total': item.product.price * item.quantity
        }
        for item in cart_items
    ]

    # Render the cart template with the cart items and total price
    return render(request, 'cart.html', {
        'cart_items': cart_items_with_totals,
        'cart_total': cart_total,
    })
    #Add to cart
@login_required
def add_to_cart(request):
    if request.method == 'POST':
        try:
            # Get product details from POST request
            product_type = request.POST.get('product_type', 'regular')
            product_id = request.POST.get('product_id')

            # Ensure the user has a customer profile
            customer, created = Customer.objects.get_or_create(user=request.user)

            # Ensure the user has an active cart or create a new one
            cart, cart_created = Cart.objects.get_or_create(customer=customer, completed=False)

            # Handle different product types
            if product_type == 'regular':
                # Regular product
                product = get_object_or_404(Product, id=product_id)
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=cart, 
                    product=product,
                    defaults={'quantity': 1}
                )
                
                if not item_created:
                    cart_item.quantity += 1
                    cart_item.save()

            elif product_type == 'flash_sale':
                # Flash Sale Product
                flash_sale_product = get_object_or_404(FlashSaleProduct, id=product_id)
                
                # Check if flash sale is currently active
                now = timezone.now()
                if not (flash_sale_product.flash_sale_start_time <= now <= flash_sale_product.flash_sale_end_time):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Flash sale has ended or not started yet.'
                    }, status=400)

                # Additional check for flash sale availability
                if flash_sale_product.available_quantity <= 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Flash sale product is sold out.'
                    }, status=400)

                # Add flash sale product to cart
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=cart, 
                    product=flash_sale_product.product,
                    defaults={'quantity': 1}
                )
                
                if not item_created:
                    cart_item.quantity += 1
                
                # Reduce available quantity
                flash_sale_product.available_quantity -= cart_item.quantity
                flash_sale_product.save()
                cart_item.save()

            elif product_type == 'new_product':
                # New Product
                new_product = get_object_or_404(NewProduct, id=product_id)
                
                # Add new product to cart
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=cart, 
                    product=new_product.product,
                    defaults={'quantity': 1}
                )
                
                if not item_created:
                    cart_item.quantity += 1
                    cart_item.save()

            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid product type.'
                }, status=400)

            # Get the updated cart item count
            cart_count = cart.items.count()

            # Return success response
            return JsonResponse({
                'status': 'success',
                'message': f'{cart_item.product.name} added to cart!',
                'cart_count': cart_count
            })

        except Product.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Product not found.'
            }, status=404)
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    # If not a POST request
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    }, status=405)

        
    
    #Remove
@login_required
def remove_from_cart(request, item_id):
    try:
        # Get the current user's active cart
        cart = Cart.objects.get(customer=request.user.customer, completed=False)
        
        # Find the specific cart item to remove
        cart_item = CartItem.objects.get(
            cart=cart, 
            id=item_id  # Use cart item ID instead of product ID for more precise removal
        )
        
        # Optional: Log the removal (for analytics or tracking)
        product_name = cart_item.product.name
        
        # Remove the item from the cart
        cart_item.delete()
        
        # Update cart total
        cart.save()
        
        # Add a success message
        messages.success(request, f'{product_name} has been removed from your cart.')
        
        return redirect('cart')
    
    except Cart.DoesNotExist:
        # Handle case where no active cart exists
        messages.error(request, 'No active cart found.')
        return redirect('store')
    
    except CartItem.DoesNotExist:
        # Handle case where the cart item doesn't exist
        messages.error(request, 'The item you tried to remove does not exist in your cart.')
        return redirect('cart')
    
    except Exception as e:
        # Catch any unexpected errors
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('cart')
    
@login_required
def checkout(request):
    # Try to get the cart for the logged-in customer and make sure it's not completed
    cart = Cart.objects.filter(customer=request.user.customer, completed=False).first()

    if not cart:
        # Redirect if no active cart exists
        return redirect('cart')  # Replace with the name of your cart page route

    # Get cart items for the existing cart
    cart_items = CartItem.objects.filter(cart=cart)

    # Calculate the total price for each cart item and the overall cart total
    cart_total = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)

    # Handle form submission
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            # Save the shipping address
            shipping_address = form.save(commit=False)
            shipping_address.customer = request.user.customer
            shipping_address.cart = cart
            shipping_address.save()

            # Create an Order instance
            order = Order.objects.create(
                customer=request.user.customer,
                total_amount=cart_total,
            )
            order.items.set(cart.items.all())  # Associate the cart items with the order
            order.save()

            # Mark the cart as completed
            cart.completed = True
            cart.save()

            # Redirect to the orders page after checkout
            return redirect('view_orders')  # Redirect to the orders view page

    else:
        form = ShippingAddressForm()

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'form': form,
    })

@login_required
def view_orders(request):
    # Fetch all orders for the logged-in customer
    orders = Order.objects.filter(customer=request.user.customer).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    # Retrieve the Order object by order_id
    order = Order.objects.get(order_id=order_id)

    # Access customer details
    customer_name = order.customer.name
    customer_email = order.customer.email  # Assuming your Customer model has an 'email' field

    # Access shipping address using the related_name 'shipping_address'
    

    # Calculate the total price for each item in the order
    order_items = []
    for item in order.items.all():
        total_price = item.product.price * item.quantity
        order_items.append({
            'item': item,
            'total_price': total_price,
        })

    # Pass the order, order items, shipping address, customer name, and customer email to the template
    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': order_items,
        'customer_name': customer_name,
        'customer_email': customer_email,
    })

@login_required
def process_payment(request, order_id):
    # Retrieve the order
    order = get_object_or_404(Order, order_id=order_id)

    # Check if the order is already paid
    if order.is_paid:
        return redirect('order_detail', order_id=order_id)

    # Process payment (this could involve integration with a payment gateway)
    if request.method == 'POST':
        # Here, you could implement payment gateway integration (Stripe, PayPal, etc.)
        payment_method = request.POST.get('payment_method')  # E.g., 'Credit Card', 'PayPal'
        payment_amount = order.total_amount  # Assuming the amount is calculated
        # Mark the order as paid and create the payment record
        order.is_paid = True
        order.save()

        payment = Payment.objects.create(
            order=order,
            user=request.user,
            payment_method=payment_method,
            payment_amount=payment_amount,
            payment_status='Completed'
        )

        return redirect('order_detail', order_id=order_id)

    # If it's not a POST request, render the payment page
    return render(request, 'process_payment.html', {'order': order})



