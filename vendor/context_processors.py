from .models import Order

def base_context(request):
    pending_count = 0
    if request.session.get("user_type") == "vendor":
        vendor_id = request.session.get("user_id")
        pending_count = Order.objects.filter(vendor_id=vendor_id, status="Pending").count()
    return {"pending_orders_count": pending_count}
