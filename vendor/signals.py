from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Order

@receiver(post_save, sender=Order)
def notify_new_order(sender, instance, created, **kwargs):
    if created and instance.status == "Pending":
        channel_layer = get_channel_layer()
        group_name = f"vendor_{instance.vendor_id}_orders"

        # Count unseen orders
        count = Order.objects.filter(
            vendor_id=instance.vendor_id,
            status="Pending",
            seen_by_vendor=False
        ).count()

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_order_count",
                "count": count
            }
        )
