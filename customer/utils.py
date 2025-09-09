from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Diamond

def merge_guest_cart_to_customer(request, customer):
    guest_cart = request.session.get("guest_cart", {})
    if not guest_cart:
        return

    cart, _ = Cart.objects.get_or_create(customer=customer)

    for diamond_id, quantity in guest_cart.items():
        diamond = get_object_or_404(Diamond, pk=diamond_id)
        item, created = CartItem.objects.get_or_create(cart=cart, diamond=diamond)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

    request.session.pop("guest_cart", None)
