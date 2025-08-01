from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404
from .forms import *
from .models import *

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            if password1 != password2:
                messages.error(request, "Passwords do not match.")
                return render(request, 'vendor/register.html', {'form': form})
            else:
                vendor = form.save(commit=False)
                vendor.password = make_password(password1)
                vendor.save()
                messages.success(request, "Registration successful. Please login.")
                return redirect('vendor:login')
    else:
        form = RegistrationForm()
    return render(request, 'vendor/register.html', {'form': form})

def edit_profile(request):
    if 'vendor_id' not in request.session:
        return redirect('login')
    vendor = Vendor.objects.get(id=request.session['vendor_id'])
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('vendor:load_diamonds')
    else:
        form = ProfileForm(instance=vendor)
    return render(request, 'vendor/edit_profile.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                vendor = Vendor.objects.get(username=username)
                if check_password(password, vendor.password):  
                    request.session['vendor_id'] = vendor.id
                    messages.success(request, "Login successful.")
                    return redirect('vendor:load_diamonds')
                else:
                    messages.error(request, "Incorrect password.")
            except Vendor.DoesNotExist:
                messages.error(request, "User does not exist.")
    else:
        form = LoginForm()
    return render(request, 'vendor/login.html', {'form': form})

def logout(request):
    if 'vendor_id' in request.session:
        request.session.flush() 
        messages.success(request, "You have been logged out.")
    return redirect('vendor:login')

def add_diamond(request):
    if 'vendor_id' not in request.session:
        return redirect('vendor:login')
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

def edit_diamond(request, sr_no):
    if 'vendor_id' not in request.session:
        return redirect('login')
    diamond = get_object_or_404(Diamond, sr_no=sr_no)
    if request.method == 'POST':
        form = DiamondForm(request.POST, instance=diamond)
        if form.is_valid():
            form.save()
            messages.success(request, "Diamond updated successfully.")
            return redirect('vendor:load_diamonds')
    else:
        form = DiamondForm(instance=diamond)
    return render(request, 'vendor/edit_diamond.html', {'form': form, 'diamond': diamond})

def delete_diamond(request, sr_no):
    if 'vendor_id' not in request.session:
        return redirect('login')
    diamond = get_object_or_404(Diamond, sr_no=sr_no)
    if request.method == 'GET':
        diamond.delete()
        messages.success(request, "Diamond deleted successfully.")
        return redirect('vendor:load_diamonds')

def load_diamonds(request):
    if 'vendor_id' not in request.session:
        return redirect('login')
    diamonds = Diamond.objects.filter(vendor_id=request.session['vendor_id'])
    return render(request, 'vendor/load_diamonds.html', {'diamonds': diamonds})