from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from vendor.models import Diamond
from .models import Cart, CartItem, Customer

def add_to_cart(request, diamond_id):
    if 'user_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, "You must be logged in as a customer to add to cart.")
        return redirect('login')

    customer = get_object_or_404(Customer, id=request.session['user_id'])
    diamond = get_object_or_404(Diamond, id=diamond_id)

    cart, created = Cart.objects.get_or_create(customer=customer)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, diamond=diamond)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{diamond} added to cart.")
    return redirect('dashboard') 