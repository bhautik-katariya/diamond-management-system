from .models import CartItem

def cart_count(request):
    count = 0
    if request.session.get("user_type") == "customer" and request.session.get("user_id"):
        try:
            count = CartItem.objects.filter(cart__customer_id=request.session["user_id"]).count()
        except:
            count = 0
    else:
        count = len(request.session.get("guest_cart", {}))
    return {"cart_count": count}