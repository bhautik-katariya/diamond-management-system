from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404
from bs4 import BeautifulSoup
import requests
from django.core.paginator import Paginator
from django.db.models import Sum
from .forms import *
from vendor.models import *
from customer.models import *
import openpyxl
from django.http import HttpResponse
from vendor.models import Diamond
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.contrib.auth.views import LogoutView
from urllib.parse import urlencode


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            customer = Customer.objects.create(
                fname=form.cleaned_data['fname'],
                lname=form.cleaned_data['lname'],
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                password=make_password(form.cleaned_data['password1']),
            )

            # Set session
            request.session['user_type'] = "customer"
            request.session['user_id'] = customer.id

            messages.success(request, f"Customer registration successful!")
            return redirect('dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'auth/register.html', {'form': form})

def vendor_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            vendor = Vendor.objects.create(
                fname=form.cleaned_data['fname'],
                lname=form.cleaned_data['lname'],
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                password=make_password(form.cleaned_data['password1']),
            )

            # Set session
            request.session['user_type'] = "vendor"
            request.session['user_id'] = vendor.id

            messages.success(request, f"Vendor registration successful!")
            return redirect('vendor:load_diamonds')
    else:
        form = RegistrationForm(initial={'user_type': 'vendor'})

    return render(request, 'auth/register.html', {'form': form, 'is_vendor_register': True})

def login(request):
    next_url = request.GET.get('next')  # Capture ?next param if present

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                customer = Customer.objects.get(username=username)
                if check_password(password, customer.password):
                    request.session['user_type'] = 'customer'
                    request.session['user_id'] = customer.id

                    # Merge guest cart with user's cart
                    guest_cart = request.session.get('guest_cart', {})
                    if guest_cart:
                        user_cart, created = Cart.objects.get_or_create(customer=customer)
                        for diamond_id, quantity in guest_cart.items():
                            try:
                                diamond = get_object_or_404(Diamond, pk=diamond_id)
                                cart_item, created = CartItem.objects.get_or_create(cart=user_cart, diamond=diamond)
                                if not created:
                                    cart_item.quantity += quantity
                                    cart_item.save()
                            except Diamond.DoesNotExist:
                                pass  # Ignore if diamond no longer exists
                        del request.session['guest_cart']

                    # Redirect back to next_url if provided, else dashboard
                    if next_url:
                        return redirect(next_url)
                    return redirect('dashboard')
                else:
                    messages.error(request, "Incorrect password.")
            except Customer.DoesNotExist:
                messages.error(request, "Customer does not exist.")
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form, 'next': next_url})
    
def vendor_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                vendor = Vendor.objects.get(username=username)
                if check_password(password, vendor.password):
                    request.session['user_type'] = 'vendor'
                    request.session['user_id'] = vendor.id
                    messages.success(request, "Vendor login successful!")
                    return redirect('vendor:load_diamonds')
                else:
                    messages.error(request, "Incorrect password.")
                    return render(request, 'auth/login.html', {'form': form, 'is_vendor_login': True})
            except Vendor.DoesNotExist:
                messages.error(request, "Vendor does not exist.")
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form, 'is_vendor_login': True})

def logout(request):
    if 'user_id' in request.session:
        request.session.flush()
        messages.success(request, f"You have been logged out.")
    return redirect('dashboard')

def edit_profile(request):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')

    if user_type == 'vendor':
        user = Vendor.objects.get(pk=user_id)
    else:
        user = Customer.objects.get(pk=user_id)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user, user_type=user_type, user_id=user_id)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('dashboard')  # or wherever you want to go after update
    else:
        form = ProfileForm(instance=user, user_type=user_type, user_id=user_id)

    return render(request, 'edit_profile.html', {'form': form, 'user_type':user_type})


def dashboard(request):
    diamonds = Diamond.objects.all().order_by('-created_at')
    
    # Get filters from query params
    shape = request.GET.getlist('shape')
    color = request.GET.getlist('color')
    clarity = request.GET.getlist('clarity')
    cut = request.GET.getlist('cut')
    lab = request.GET.getlist('lab')
    min_carat = request.GET.get('min_carat')
    max_carat = request.GET.get('max_carat')

    # Apply filters
    if shape:
        diamonds = diamonds.filter(shape__in=shape)
    if color:
        diamonds = diamonds.filter(color__in=color)
    if clarity:
        diamonds = diamonds.filter(clarity__in=clarity)
    if cut:
        diamonds = diamonds.filter(cut__in=cut)
    if lab:
        diamonds = diamonds.filter(lab__in=lab)
    if min_carat:
        diamonds = diamonds.filter(carat__gte=min_carat)
    if max_carat:
        diamonds = diamonds.filter(carat__lte=max_carat)

    # Sorting
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        diamonds = diamonds.order_by('price_per_carat')
    elif sort == 'price_desc':
        diamonds = diamonds.order_by('-price_per_carat')
    elif sort == 'carat_asc':
        diamonds = diamonds.order_by('carat')
    elif sort == 'carat_desc':
        diamonds = diamonds.order_by('-carat')
    elif sort == 'color_asc':
        diamonds = diamonds.order_by('color')
    elif sort == 'color_desc':
        diamonds = diamonds.order_by('-color')
    elif sort == 'clarity_asc':
        diamonds = diamonds.order_by('clarity')
    elif sort == 'clarity_desc':
        diamonds = diamonds.order_by('-clarity')

    # Stats
    total_stock = diamonds.count()
    total_carat = diamonds.aggregate(Sum('carat'))['carat__sum'] or 0
    total_amount = diamonds.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Pagination
    paginator = Paginator(diamonds, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Active filters for checkbox state
    active_filters = {
        "shape": shape,
        "color": color,
        "clarity": clarity,
        "cut": cut,
        "lab": lab,
    }

    # Filter groups to loop over in template
    filter_groups = [
        ("Shape", Diamond.SHAPE, "shape"),
        ("Color", Diamond.COLOUR, "color"),
        ("Clarity", Diamond.CLARITY, "clarity"),
        ("Cut", Diamond.CUT, "cut"),
        ("Lab", Diamond.LAB, "lab"),
    ]

    # Keep raw params (no backend cleaning)
    get_params = request.GET.urlencode()

    context = {
        'diamonds': page_obj.object_list,
        'page_obj': page_obj,
        'active_filters': active_filters,
        'filter_groups': filter_groups,
        'total_stock': total_stock,
        'total_carat': round(total_carat, 2),
        'total_amount': round(total_amount, 2),
        'get_params': get_params,
    }

    return render(request, 'dashboard.html', context)

def diamond_detail(request, id):
    diamond = get_object_or_404(Diamond, pk=id)
    from_order = request.GET.get('from_order', False)

    image_url = None

    if diamond.photo:
        try:
            response = requests.get(diamond.photo, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for og:image meta tag
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.has_attr('content'):
                    image_url = og_image['content']

        except Exception as e:
            print("Error fetching image from meta:", e)

    return render(request, 'diamond_detail.html', {
        'diamond': diamond,
        'image_url': image_url,
        'from_order': from_order
    })

@csrf_exempt
def download_diamonds_excel(request):
    if request.method == 'POST':
        ids_str = request.POST.get('diamond_ids', '')
        ids = [int(i) for i in ids_str.split(',') if i.strip().isdigit()]
        diamonds = Diamond.objects.filter(id__in=ids) if ids else Diamond.objects.none()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Diamonds"

        # Get all field names from the model, excluding created_at and id
        fields = [field for field in Diamond._meta.get_fields() if not field.many_to_many and not field.one_to_many and field.name not in ('id', 'vendor', 'created_at')]
        headers = ['Sr No'] + [field.verbose_name.title() for field in fields]
        ws.append(headers)

        for index, d in enumerate(diamonds, start=1):
            row = [index]
            for field in fields:
                value = getattr(d, field.name)
                # For ForeignKey, get readable string
                if field.is_relation and field.many_to_one:
                    value = str(value) if value else ''
                # For display fields, get the display name
                elif field.name == 'shape':
                    value = d.get_shape_display()
                elif field.name == 'cut':
                    value = d.get_cut_display()
                elif field.name == 'polish':
                    value = d.get_polish_display()
                elif field.name == 'symmetry':
                    value = d.get_symmetry_display()
                # Remove timezone from datetime/time fields
                if isinstance(value, (datetime.datetime, datetime.time)) and getattr(value, 'tzinfo', None) is not None:
                    value = value.replace(tzinfo=None)
                row.append(value)
            ws.append(row)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=diamonds.xlsx'
        wb.save(response)
        return response
    return HttpResponse(status=405)
  
class AdminLogoutView(LogoutView):
    next_page = 'admin:login'
    def get(self, request, *args, **kwargs):   # allow GET request
        return self.post(request, *args, **kwargs)