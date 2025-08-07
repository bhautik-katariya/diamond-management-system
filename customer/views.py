from django.shortcuts import redirect,render, get_object_or_404
from django.contrib import messages
from vendor.models import Diamond
from .models import Cart, CartItem, Customer
from django.db import IntegrityError
from django.core.mail import send_mail

def add_to_cart(request, diamond_id):
    if 'user_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, "You must be logged in as a customer to add to cart.")
        return redirect('login')

    customer = get_object_or_404(Customer, pk=request.session['user_id'])
    diamond = get_object_or_404(Diamond, pk=diamond_id)

    cart, created = Cart.objects.get_or_create(customer=customer)
    try:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, diamond=diamond)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        messages.success(request, f"Diamond {diamond.stock_id} added to cart.")
        print(f"Customer '{customer.username}' added Diamond '{diamond.stock_id}' to cart. Vendor: {diamond.vendor.fname}")
        # send_mail(
        #     subject="New Diamond Added to Cart",
        #     message=f"Customer {customer.username} ({customer.email}) added your diamond {diamond.stock_id} to their cart.",
        #     from_email="yourapp@example.com",
        #     recipient_list=[diamond.vendor.email],  # Assuming `diamond.vendor.email` exists
        # )
    except IntegrityError:
        messages.error(request, "This diamond is already in your cart.")
    return redirect('dashboard') 

def view_cart(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, "Please log in as a customer to view your cart.")
        return redirect('login')

    customer = get_object_or_404(Customer, pk=request.session['user_id'])
    cart, created = Cart.objects.get_or_create(customer=customer)
    
    return render(request, 'customer/cart.html', {
        'cart': cart,
    })

# def remove_from_cart(request, item_id):
#     if 'user_id' not in request.session or request.session.get('user_type') != 'customer':
#         messages.error(request, "You must be logged in as a customer to remove items.")
#         return redirect('login')

#     item = get_object_or_404(CartItem, pk=item_id)
#     if item.cart.customer.id == request.session['user_id']:
#         item.delete()
#         messages.success(request, "Item removed from cart.")
#     else:
#         messages.error(request, "You are not authorized to remove this item.")
#     return redirect('customer:view_cart')

def remove_from_cart(request, item_id):
    if 'user_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, "You must be logged in as a customer to remove items.")
        return redirect('login')

    item = get_object_or_404(CartItem, pk=item_id)

    if item.cart.customer.id == request.session['user_id']:
        item.delete()
        messages.success(request, "Item removed from cart.")
    else:
        messages.error(request, "You are not authorized to remove this item.")

    return redirect('customer:view_cart')

def increase_quantity(request, item_id):
    if request.method == 'POST' and 'user_id' in request.session and request.session.get('user_type') == 'customer':
        item = get_object_or_404(CartItem, pk=item_id)
        if item.cart.customer.id == request.session['user_id']:
            item.quantity += 1
            item.save()
            messages.success(request, f"Increased quantity for {item.diamond.stock_id}.")
        else:
            messages.error(request, "You are not authorized to update this item.")
    else:
        messages.error(request, "Invalid request.")
    return redirect('customer:view_cart')

def decrease_quantity(request, item_id):
    if request.method == 'POST' and 'user_id' in request.session and request.session.get('user_type') == 'customer':
        item = get_object_or_404(CartItem, pk=item_id)
        if item.cart.customer.id == request.session['user_id']:
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
                messages.success(request, f"Decreased quantity for {item.diamond.stock_id}.")
            else:
                item.delete()
                messages.success(request, f"Removed {item.diamond.stock_id} from cart.")
        else:
            messages.error(request, "You are not authorized to update this item.")
    else:
        messages.error(request, "Invalid request.")
    return redirect('customer:view_cart')