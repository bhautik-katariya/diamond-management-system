from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Sum
from .forms import *
from vendor.models import *
from customer.models import *

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user_type = form.cleaned_data['user_type']
            Model = Vendor if user_type == 'vendor' else Customer

            user = Model.objects.create(
                fname=form.cleaned_data['fname'],
                lname=form.cleaned_data['lname'],
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                password=make_password(form.cleaned_data['password1']),
            )

            # Set session
            request.session['user_type'] = user_type
            request.session['user_id'] = user.id

            messages.success(request, f"{user_type.capitalize()} registration successful!")
            return redirect('vendor:load_diamonds' if user_type == 'vendor' else 'dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'auth/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user_type = form.cleaned_data['user_type']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            if user_type == 'vendor':
                try:
                    vendor = Vendor.objects.get(username=username)
                    if check_password(password, vendor.password):
                        request.session['user_type'] = 'vendor'
                        request.session['user_id'] = vendor.id
                        messages.success(request, "Vendor login successful!")
                        return redirect('vendor:load_diamonds')
                    else:
                        messages.error(request, "Incorrect password.")
                except Vendor.DoesNotExist:
                    messages.error(request, "Vendor does not exist.")
            else:
                try:
                    customer = Customer.objects.get(username=username)
                    if check_password(password, customer.password):
                        request.session['user_type'] = 'customer'
                        request.session['user_id'] = customer.id
                        messages.success(request, "Customer login successful!")
                        return redirect('dashboard')
                    else:
                        messages.error(request, "Incorrect password.")
                except Customer.DoesNotExist:
                    messages.error(request, "Customer does not exist.")
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

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
    diamonds = Diamond.objects.all().order_by('id')

    # Get filters from query params
    shape = request.GET.getlist('shape')
    color = request.GET.getlist('color')
    clarity = request.GET.getlist('clarity')
    cut = request.GET.getlist('cut')
    polish = request.GET.getlist('polish')
    symmetry = request.GET.getlist('symmetry')
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
    if polish:
        diamonds = diamonds.filter(polish__in=polish)
    if symmetry:
        diamonds = diamonds.filter(symmetry__in=symmetry)
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
    paginator = Paginator(diamonds, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Active filters for checkbox state
    active_filters = {
        "shape": shape,
        "color": color,
        "clarity": clarity,
        "cut": cut,
        "polish": polish,
        "symmetry": symmetry,
        "lab": lab,
    }

    # Filter groups to loop over in template
    filter_groups = [
        ("Shape", Diamond.SHAPE, "shape"),
        ("Color", Diamond.COLOUR, "color"),
        ("Clarity", Diamond.CLARITY, "clarity"),
        ("Cut", Diamond.CUT, "cut"),
        ("Polish", Diamond.POLISH, "polish"),
        ("Symmetry", Diamond.SYMMETRY, "symmetry"),
        ("Lab", Diamond.LAB, "lab"),
    ]

    # Add get_params for pagination links
    get_params = request.GET.copy()
    if 'page' in get_params:
        get_params.pop('page')
    get_params_str = get_params.urlencode()
    context = {
        'diamonds': page_obj.object_list,
        'page_obj': page_obj,
        'active_filters': active_filters,
        'filter_groups': filter_groups,
        'total_stock': total_stock,
        'total_carat': round(total_carat, 2),
        'total_amount': round(total_amount, 2),
        'get_params': get_params_str,
    }

    return render(request, 'dashboard.html', context)

def diamond_detail(request, id):
    from django.shortcuts import get_object_or_404
    diamond = get_object_or_404(Diamond, pk=id)
    return render(request, 'diamond_detail.html', {'diamond': diamond})

