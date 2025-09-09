from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import OrderItem

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
