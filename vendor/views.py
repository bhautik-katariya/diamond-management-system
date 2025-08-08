from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .forms import *
from .models import *

def add_diamond(request):
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        form = DiamondForm(request.POST)
        if form.is_valid():
            diamond = form.save(commit=False)
            diamond.vendor = Vendor.objects.get(pk=request.session['user_id'])
            diamond.save()
            messages.success(request, "Diamond added successfully.")
            return redirect('vendor:load_diamonds')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = DiamondForm()
    return render(request, 'vendor/add_diamond.html', {'form': form})

def edit_diamond(request, id):
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')
    diamond = get_object_or_404(Diamond, pk=id)
    if request.method == 'POST':
        form = DiamondForm(request.POST, instance=diamond)
        if form.is_valid():
            form.save()
            messages.success(request, "Diamond updated successfully.")
            return redirect('vendor:load_diamonds')
    else:
        form = DiamondForm(instance=diamond)
    return render(request, 'vendor/edit_diamond.html', {'form': form, 'diamond': diamond})

def delete_diamond(request, id):
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')
    diamond = get_object_or_404(Diamond, pk=id)
    if request.method == 'GET':
        diamond.delete()
        messages.success(request, "Diamond deleted successfully.")
        return redirect('vendor:load_diamonds')

def load_diamonds(request):
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')   
    diamond_qs = Diamond.objects.filter(vendor_id=request.session['user_id']).order_by('-created_at')
    paginator = Paginator(diamond_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'vendor/load_diamonds.html', {
        'diamonds': page_obj.object_list,
        'page_obj': page_obj,
    })

def view_orders(request):
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')
    vendor_id = request.session['user_id']
    orders_qs = Order.objects.filter(vendor_id=vendor_id).order_by('-created_at').prefetch_related('items', 'customer')
    paginator = Paginator(orders_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'vendor/order.html', {
        'orders': page_obj.object_list,
        'page_obj': page_obj,
    })