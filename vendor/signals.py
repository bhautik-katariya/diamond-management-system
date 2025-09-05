from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import OrderItem

@receiver(post_save, sender=OrderItem)
def notify_orderitem_status(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    group_name = f"vendor_{instance.order.vendor_id}_orders"

    # Count pending items for this vendor
    from .models import OrderItem
    count = OrderItem.objects.filter(
        order__vendor_id=instance.order.vendor_id,
        status="Pending"
    ).count()

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_order_count",
            "count": count,
        }
    )
