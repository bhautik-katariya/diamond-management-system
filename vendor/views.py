from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .forms import *
from .models import *

def add_diamond(request):
    if 'vendor_id' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        form = DiamondForm(request.POST)
        if form.is_valid():
            diamond = form.save(commit=False)
            diamond.vendor = Vendor.objects.get(id=request.session['vendor_id'])
            diamond.save()
            messages.success(request, "Diamond added successfully.")
            return redirect('vendor:load_diamonds')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = DiamondForm()
    return render(request, 'vendor/add_diamond.html', {'form': form})

def edit_diamond(request, id):
    if 'vendor_id' not in request.session:
        return redirect('login')
    diamond = get_object_or_404(Diamond, id=id)
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
    if 'vendor_id' not in request.session:
        return redirect('login')
    diamond = get_object_or_404(Diamond, id=id)
    if request.method == 'GET':
        diamond.delete()
        messages.success(request, "Diamond deleted successfully.")
        return redirect('vendor:load_diamonds')

def load_diamonds(request):
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')   
    diamonds = Diamond.objects.filter(vendor_id=request.session['user_id'])
    return render(request, 'vendor/load_diamonds.html', {'diamonds': diamonds})