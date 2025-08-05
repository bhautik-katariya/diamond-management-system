from django.db import models

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
