from .models import OrderItem

def base_context(request):
    vendor_id = request.session.get("user_id")
    pending_count = 0
    if request.session.get("user_type") == "vendor" and vendor_id:
        pending_count = OrderItem.objects.filter(
            order__vendor_id=vendor_id,
            status="Pending"
        ).count()

    # Apply cap for UI consistency
    display_count = "9+" if pending_count > 9 else pending_count

    return {
        "pending_orders_count": display_count,
        "raw_pending_orders_count": pending_count,  # optional, if you need exact number in backend
    }


