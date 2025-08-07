from django.db import models
from vendor.models import Diamond

# Create your models here.

class Customer(models.Model):
    fname = models.CharField(max_length=255, blank=False, null=False)
    lname = models.CharField(max_length=255, blank=False, null=False)
    username = models.CharField(max_length=150, unique=True, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone = models.CharField(max_length=15, unique=True, blank=False, null=False)
    password = models.CharField(max_length=128, blank=False, null=False)

    def __str__(self):
        return f"{self.fname} {self.lname}"

class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.customer.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    diamond = models.ForeignKey(Diamond, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'diamond')

    def __str__(self):
        return f"{self.quantity} x diamond in {self.cart}"

    @property
    def line_total(self):
        return float(self.diamond.price_per_carat) * float(self.diamond.carat) * self.quantity