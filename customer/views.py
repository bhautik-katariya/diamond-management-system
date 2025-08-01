from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Sum
from vendor.models import Diamond

def dashboard(request):
    diamonds = Diamond.objects.all().order_by('sr_no')

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

    context = {
        'diamonds': page_obj.object_list,
        'page_obj': page_obj,
        'active_filters': active_filters,
        'filter_groups': filter_groups,
        'total_stock': total_stock,
        'total_carat': round(total_carat, 2),
        'total_amount': round(total_amount, 2),
    }

    return render(request, 'customer/dashboard.html', context)

def diamond_detail(request, sr_no):
    from django.shortcuts import get_object_or_404
    diamond = get_object_or_404(Diamond, sr_no=sr_no)
    return render(request, 'customer/diamond_detail.html', {'diamond': diamond})
