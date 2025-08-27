import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.vendor_id = self.scope["url_route"]["kwargs"]["vendor_id"]
        self.group_name = f"vendor_{self.vendor_id}_orders"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # handle count messages
    async def send_order_count(self, event):
        await self.send(text_data=json.dumps({
            "count": event["count"]
        }))

    # still keep this if you want "new order received"
    async def new_order(self, event):
        await self.send(text_data=json.dumps({
            "order_id": event["order_id"]
        }))
