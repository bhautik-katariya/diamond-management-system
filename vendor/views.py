from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from .forms import *
from .models import *

# Mapping dictionary for field values
rawMappings = {
    'shape': {
        "asscher": "AS",
        "baguette": "BG",
        "cushion": "CS",
        "emerald": "EM",
        "heart": "HT",
        "marquise": "MQ",
        "old": "OLD",
        "oval": "OVL",
        "pear": "PR",
        "princess": "PRS",
        "radiant": "RDNT",
        "round": "RD",
        "square": "SQ",
        "taper": "TP",
        "trillion": "TR",
        "other": "OT"
    },
    'type': {
        "cvd": "CVD",
        "hpht": "HPHT"
    },
    'lab': {
        "igi": "IGI",
        "gia": "GIA"
    },
    'color': {
        "d": "D", "e": "E", "f": "F", "g": "G", "h": "H", "i": "I", "j": "J",
        "fancy blue": "FB",
        "fancy intense blue": "FIB",
        "light blue": "LB",
        "fancy pink": "FP",
        "fancy intense pink": "FIP",
        "light pink": "LP"
    },
    'clarity': {
        "fl": "FL", "if": "IF", "vvs1": "VVS1", "vvs2": "VVS2",
        "vs1": "VS1", "vs2": "VS2",
        "si1": "SI1", "si2": "SI2", "si3": "SI3",
        "i1": "I1", "i2": "I2", "i3": "I3"
    },
    'cut': {
        "ideal": "ID",
        "excellent": "EX",
        "very good": "VG",
        "good": "GD",
        "fair": "FR"
    },
    'polish': {
        "ideal": "ID",
        "excellent": "EX",
        "very good": "VG",
        "good": "GD",
        "fair": "FR"
    },
    'symmetry': {
        "ideal": "ID",
        "excellent": "EX",
        "very good": "VG",
        "good": "GD",
        "fair": "FR"
    }
}

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

def add_multiple_diamonds(request):
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Handle both form data and JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                multiple_diamonds = data.get('multiple_diamonds')
            else:
                multiple_diamonds = request.POST.get('multiple_diamonds')
                if multiple_diamonds:
                    multiple_diamonds = json.loads(multiple_diamonds)
            
            if multiple_diamonds:
                vendor = Vendor.objects.get(pk=request.session['user_id'])
                success_count = 0
                error_count = 0
                
                for diamond_data in multiple_diamonds:
                    try:
                        # Create form data for each diamond
                        form_data = {}
                        for key, value in diamond_data.items():
                            if key in ['type', 'lab', 'color', 'clarity', 'cut', 'polish', 'symmetry', 'fluorescence', 'shape']:
                                # Handle choice fields
                                normalized_value = str(value).strip().lower()
                                if key in rawMappings:
                                    mapped_value = rawMappings[key].get(normalized_value)
                                    if mapped_value:
                                        form_data[key] = mapped_value
                                    elif key == 'shape':
                                        form_data[key] = 'OT'  # Default to "other" for unrecognized shapes
                                    else:
                                        form_data[key] = value
                                else:
                                    form_data[key] = value
                            else:
                                form_data[key] = value
                        
                        # Create and save diamond
                        form = DiamondForm(form_data)
                        if form.is_valid():
                            diamond = form.save(commit=False)
                            diamond.vendor = vendor
                            diamond.save()
                            success_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        error_count += 1
                
                # Return JSON response for AJAX requests
                if request.content_type == 'application/json':
                    if success_count > 0:
                        return JsonResponse({
                            'success': True,
                            'success_count': success_count,
                            'error_count': error_count,
                            'message': f"Successfully added {success_count} diamonds."
                        })
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': f"Failed to add any diamonds. {error_count} errors occurred."
                        })
                else:
                    # Handle form submission (fallback)
                    if success_count > 0:
                        messages.success(request, f"Successfully added {success_count} diamonds.")
                    if error_count > 0:
                        messages.warning(request, f"Failed to add {error_count} diamonds. Please check the data format.")
                    return redirect('vendor:load_diamonds')
                
        except json.JSONDecodeError:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': 'Invalid JSON format in the uploaded file.'})
            else:
                messages.error(request, "Invalid JSON format in the uploaded file.")
                return redirect('vendor:add_diamond')
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': f'Error processing diamonds: {str(e)}'})
            else:
                messages.error(request, f"Error processing diamonds: {str(e)}")
                return redirect('vendor:add_diamond')
    
    return redirect('vendor:add_diamond')

def update_multiple_diamonds(request):
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Handle both form data and JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                multiple_diamonds = data.get('multiple_diamonds')
            else:
                multiple_diamonds = request.POST.get('multiple_diamonds')
                if multiple_diamonds:
                    multiple_diamonds = json.loads(multiple_diamonds)
            
            if multiple_diamonds:
                vendor = Vendor.objects.get(pk=request.session['user_id'])
                success_count = 0
                error_count = 0
                
                for diamond_data in multiple_diamonds:
                    try:
                        # Check if diamond exists by stock_id
                        stock_id = diamond_data.get('stock_id')
                        if stock_id:
                            diamond = Diamond.objects.filter(stock_id=stock_id, vendor=vendor).first()
                            if diamond:
                                # Update existing diamond
                                form_data = {}
                                for key, value in diamond_data.items():
                                    if key in ['type', 'lab', 'color', 'clarity', 'cut', 'polish', 'symmetry', 'fluorescence', 'shape']:
                                        # Handle choice fields
                                        normalized_value = str(value).strip().lower()
                                        if key in rawMappings:
                                            mapped_value = rawMappings[key].get(normalized_value)
                                            if mapped_value:
                                                form_data[key] = mapped_value
                                            elif key == 'shape':
                                                form_data[key] = 'OT'  # Default to "other" for unrecognized shapes
                                            else:
                                                form_data[key] = value
                                        else:
                                            form_data[key] = value
                                    else:
                                        form_data[key] = value
                                
                                # Create form with existing diamond instance
                                form = DiamondForm(form_data, instance=diamond)
                                if form.is_valid():
                                    form.save()
                                    success_count += 1
                                else:
                                    error_count += 1
                            else:
                                error_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        error_count += 1
                
                # Return JSON response for AJAX requests
                if request.content_type == 'application/json':
                    if success_count > 0:
                        return JsonResponse({
                            'success': True,
                            'success_count': success_count,
                            'error_count': error_count,
                            'message': f"Successfully updated {success_count} diamonds."
                        })
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': f"Failed to update any diamonds. {error_count} errors occurred."
                        })
                else:
                    # Handle form submission (fallback)
                    if success_count > 0:
                        messages.success(request, f"Successfully updated {success_count} diamonds.")
                    if error_count > 0:
                        messages.warning(request, f"Failed to update {error_count} diamonds. Please check the data format.")
                    return redirect('vendor:load_diamonds')
            else:
                if request.content_type == 'application/json':
                    return JsonResponse({'success': False, 'error': 'No diamond data provided.'})
                else:
                    messages.error(request, "No diamond data provided.")
                    return redirect('vendor:load_diamonds')
                
        except json.JSONDecodeError as e:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': f'Invalid JSON format: {str(e)}'})
            else:
                messages.error(request, f"Invalid JSON format: {str(e)}")
                return redirect('vendor:load_diamonds')
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': f'Error processing diamonds: {str(e)}'})
            else:
                messages.error(request, f"Error processing diamonds: {str(e)}")
                return redirect('vendor:load_diamonds')
    
    return redirect('vendor:load_diamonds')