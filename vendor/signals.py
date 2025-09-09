from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Vendor, OrderItem
from allauth.account.signals import user_signed_up, user_logged_in
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string

def broadcast_pending_count(vendor_id):
    """Send exact pending order count for a vendor."""
    channel_layer = get_channel_layer()
    from .models import OrderItem
    pending_count = OrderItem.objects.filter(
        order__vendor_id=vendor_id,
        status="Pending"
    ).count()

    async_to_sync(channel_layer.group_send)(
        f"orders_{vendor_id}",
        {
            "type": "send_order_count",
            "count": pending_count,  # exact number
        }
    )

@receiver(post_save, sender=OrderItem)
def orderitem_saved(sender, instance, **kwargs):
    broadcast_pending_count(instance.order.vendor_id)

@receiver(post_delete, sender=OrderItem)
def orderitem_deleted(sender, instance, **kwargs):
    broadcast_pending_count(instance.order.vendor_id)

def _ensure_vendor(request, user):
    role = request.session.get("login_role", "customer")
    if role != "vendor":
        return

    email = user.email or ""
    base_username = user.username or (email.split("@")[0] if email else f"user{user.id}")
    fname = user.first_name or (user.get_full_name().split(" ")[0] or base_username)
    lname = user.last_name or (" ".join(user.get_full_name().split(" ")[1:]) if user.get_full_name() else "")

    phone = f"google-{user.id}"
    dummy_hashed_pwd = make_password(get_random_string(20))

    vendor, _ = Vendor.objects.get_or_create(
        email=email,
        defaults={
            "fname": fname,
            "lname": lname,
            "username": base_username,
            "phone": phone,
            "password": dummy_hashed_pwd,
        },
    )

    request.session["user_type"] = "vendor"
    request.session["user_id"] = vendor.id

@receiver(user_signed_up)
def on_google_signed_up(request, user, **kwargs):
    _ensure_vendor(request, user)

@receiver(user_logged_in)
def on_google_logged_in(request, user, **kwargs):
    _ensure_vendor(request, user)