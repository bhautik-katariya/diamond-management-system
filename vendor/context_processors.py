from .models import OrderItem

def base_context(request):
    vendor_id = request.session.get("user_id")
    pending_count = 0
    if request.session.get("user_type") == "vendor" and vendor_id:
        pending_count = OrderItem.objects.filter(
            order__vendor_id=vendor_id,
            status="Pending",
            order__seen=False
        ).count()
    return {"pending_orders_count": pending_count}

