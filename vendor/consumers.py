import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Order

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.vendor_id = self.scope["url_route"]["kwargs"]["vendor_id"]
        self.group_name = f"vendor_{self.vendor_id}_orders"

        # Join vendor group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # No need to handle vendor -> server messages here
        pass

    async def send_order_count(self, event):
        count = event["count"]
        await self.send(text_data=json.dumps({"count": count}))
