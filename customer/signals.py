from django.dispatch import receiver
from allauth.account.signals import user_signed_up, user_logged_in
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from .models import Customer
from .utils import merge_guest_cart_to_customer

def _ensure_customer(request, user):
    role = request.session.get("login_role", "customer")
    if role != "customer":
        return

    email = user.email or ""
    base_username = user.username or (email.split("@")[0] if email else f"user{user.id}")
    fname = user.first_name or (user.get_full_name().split(" ")[0] or base_username)
    lname = user.last_name or (" ".join(user.get_full_name().split(" ")[1:]) if user.get_full_name() else "")

    # Uniques & required fields
    phone = f"google-{user.id}"
    dummy_hashed_pwd = make_password(get_random_string(20))  # non-usable

    customer, _ = Customer.objects.get_or_create(
        email=email,
        defaults={
            "fname": fname,
            "lname": lname,
            "username": base_username,
            "phone": phone,
            "password": dummy_hashed_pwd,
        },
    )

    # Sessions like your manual login
    request.session["user_type"] = "customer"
    request.session["user_id"] = customer.id

    # Merge guest cart on every login to be safe
    merge_guest_cart_to_customer(request, customer)

@receiver(user_signed_up)
def on_google_signed_up(request, user, **kwargs):
    _ensure_customer(request, user)

@receiver(user_logged_in)
def on_google_logged_in(request, user, **kwargs):
    _ensure_customer(request, user)
