from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from vendor.models import Diamond, Order, OrderItem
from .models import Cart, CartItem, Customer
from django.db import IntegrityError
from django.core.paginator import Paginator

def add_to_cart(request, diamond_id):
    diamond = get_object_or_404(Diamond, pk=diamond_id)

    if request.session.get('user_type') == 'customer' and 'user_id' in request.session:
        # User is logged in
        customer = get_object_or_404(Customer, pk=request.session['user_id'])
        cart, created = Cart.objects.get_or_create(customer=customer)
        try:
            cart_item, created = CartItem.objects.get_or_create(cart=cart, diamond=diamond)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            messages.success(request, f"Diamond {diamond.stock_id} added to your cart.")
        except IntegrityError:
            messages.error(request, "This diamond is already in your cart.")
    else:
        # User is not logged in (guest cart)
        guest_cart = request.session.get('guest_cart', {})
        diamond_id_str = str(diamond_id)
        guest_cart[diamond_id_str] = guest_cart.get(diamond_id_str, 0) + 1
        request.session['guest_cart'] = guest_cart
        messages.success(request, f"Diamond {diamond.stock_id} added to your cart.")

    # Redirect to the same page as before
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    else:
        # Fallback to HTTP_REFERER or dashboard
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect('dashboard')

def view_cart(request):
    cart_items = []
    if request.session.get('user_type') == 'customer' and 'user_id' in request.session:
        # Logged-in user's cart
        customer = get_object_or_404(Customer, pk=request.session['user_id'])
        cart, created = Cart.objects.get_or_create(customer=customer)
        cart_items = cart.items.all()
    else:
        # Guest cart
        guest_cart = request.session.get('guest_cart', {})
        for diamond_id, quantity in guest_cart.items():
            try:
                diamond = get_object_or_404(Diamond, pk=diamond_id)
                # Create a temporary object to represent the cart item
                cart_items.append({'diamond': diamond, 'quantity': quantity, 'line_total': float(diamond.price_per_carat) * float(diamond.carat) * quantity, 'id': diamond_id})
            except Diamond.DoesNotExist:
                # Remove diamond from guest cart if it no longer exists
                del request.session['guest_cart'][diamond_id]
        cart = None
        request.session.modified = True

    # Apply pagination to cart_items
    paginator = Paginator(list(cart_items), 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customer/cart.html', {
        'cart': cart,
        'page_obj': page_obj,
        'paged_items': page_obj.object_list,
    })

def remove_from_cart(request, item_id):
    if request.session.get('user_type') == 'customer' and 'user_id' in request.session:
        # Customer cart
        item = get_object_or_404(CartItem, pk=item_id, cart__customer_id=request.session['user_id'])
        item.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "item_id": item_id,
                "removed": True,
            })
        messages.success(request, "Item removed from your cart.")
    else:
        # Guest cart
        guest_cart = request.session.get('guest_cart', {})
        if str(item_id) in guest_cart:
            del guest_cart[str(item_id)]
            request.session['guest_cart'] = guest_cart
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "item_id": item_id,
                    "removed": True,
                })
            messages.success(request, "Item removed from your cart.")
        else:
            messages.error(request, "Item not found in your cart.")
    return redirect('customer:view_cart')

def increase_quantity(request, item_id):
    if request.session.get('user_type') == 'customer' and 'user_id' in request.session:
        # Customer cart
        item = get_object_or_404(CartItem, pk=item_id, cart__customer_id=request.session['user_id'])
        item.quantity += 1
        item.save()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "item_id": item.id,
                "quantity": item.quantity,
                "line_total": float(item.line_total),
            })
        messages.success(request, f"Increased quantity for {item.diamond.stock_id}.")
        return redirect('customer:view_cart')

    else:
        # Guest cart
        guest_cart = request.session.get('guest_cart', {})
        if str(item_id) in guest_cart:
            guest_cart[str(item_id)] += 1
            request.session['guest_cart'] = guest_cart
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                diamond = get_object_or_404(Diamond, pk=item_id)
                line_total = float(diamond.price_per_carat) * float(diamond.carat) * guest_cart[str(item_id)]
                return JsonResponse({
                    "success": True,
                    "item_id": item_id,
                    "quantity": guest_cart[str(item_id)],
                    "line_total": line_total,
                })
            messages.success(request, "Increased quantity in your cart.")
        else:
            messages.error(request, "Item not found in your cart.")
        return redirect('customer:view_cart')

def decrease_quantity(request, item_id):
    if request.session.get('user_type') == 'customer' and 'user_id' in request.session:
        # Customer cart
        item = get_object_or_404(CartItem, pk=item_id, cart__customer_id=request.session['user_id'])
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "item_id": item.id,
                    "quantity": item.quantity,
                    "line_total": float(item.line_total),
                })
            messages.success(request, f"Decreased quantity for {item.diamond.stock_id}.")
        else:
            item.delete()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "item_id": item_id,
                    "removed": True,
                })
            messages.success(request, f"Removed {item.diamond.stock_id} from your cart.")
        return redirect('customer:view_cart')

    else:
        # Guest cart
        guest_cart = request.session.get('guest_cart', {})
        if str(item_id) in guest_cart:
            if guest_cart[str(item_id)] > 1:
                guest_cart[str(item_id)] -= 1
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    diamond = get_object_or_404(Diamond, pk=item_id)
                    line_total = float(diamond.price_per_carat) * float(diamond.carat) * guest_cart[str(item_id)]
                    return JsonResponse({
                        "success": True,
                        "item_id": item_id,
                        "quantity": guest_cart[str(item_id)],
                        "line_total": line_total,
                    })
                messages.success(request, "Decreased quantity in your cart.")
            else:
                del guest_cart[str(item_id)]
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({
                        "success": True,
                        "item_id": item_id,
                        "removed": True,
                    })
                messages.success(request, "Removed item from your cart.")
            request.session['guest_cart'] = guest_cart
        else:
            messages.error(request, "Item not found in your cart.")
        return redirect('customer:view_cart')


def checkout(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, "Please log in as a customer to checkout.")
        login_url = f"{reverse('login')}?next={reverse('checkout')}"
        return redirect(login_url)

    customer = get_object_or_404(Customer, pk=request.session['user_id'])
    cart, created = Cart.objects.get_or_create(customer=customer)
    cart_items = cart.items.all()
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('customer:view_cart')

    # Group items by vendor
    vendor_items = {}
    for item in cart_items:
        vendor = item.diamond.vendor
        vendor_items.setdefault(vendor, []).append(item)

    # Create an order for each vendor
    for vendor, items in vendor_items.items():
        order = Order.objects.create(customer=customer, vendor=vendor)
        for item in items:
            OrderItem.objects.create(
                order=order,
                diamond=item.diamond,
                quantity=item.quantity,
                price_per_carat=item.diamond.price_per_carat,
                line_total=item.line_total
            )
            item.delete()  # Remove from cart
            
    channel_layer = get_channel_layer()
    pending_count = OrderItem.objects.filter(
        order__vendor=order.vendor,
        status="Pending",
        order__seen=False
    ).count()

    async_to_sync(channel_layer.group_send)(
        f"vendor_{order.vendor.id}_orders",
        {
            "type": "send_order_count",
            "count": pending_count
        }
    )

    messages.success(request, "Order placed successfully!")
    return render(request, 'customer/order_confirmation.html')
