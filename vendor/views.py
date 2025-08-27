from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.http import JsonResponse
import requests
import json
import ijson
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
        page = request.GET.get('page', 1)
        return redirect(f"{reverse('vendor:load_diamonds')}?page={page}")

def load_diamonds(request):
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')   
    diamond_qs = Diamond.objects.filter(vendor_id=request.session['user_id']).order_by('-created_at')
    paginator = Paginator(diamond_qs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'vendor/load_diamonds.html', {
        'diamonds': page_obj.object_list,
        'page_obj': page_obj,
    })

def _process_multiple_diamonds_list(multiple_diamonds, vendor, batch_size=1000):
    """Normalize, validate, and bulk save a list of diamond dicts.
    Returns a tuple: (success_count, error_count).
    """
    success_count = 0
    error_count = 0
    
    # Adjust batch size based on dataset size for optimal performance
    if len(multiple_diamonds) > 10000:
        batch_size = 500  # Smaller batches for very large datasets
    elif len(multiple_diamonds) > 5000:
        batch_size = 750
    else:
        batch_size = 1000
    
    print(f"Processing {len(multiple_diamonds)} diamonds in batches of {batch_size}")
    
    # Debug: Show sample of first diamond data
    if multiple_diamonds:
        print(f"Sample diamond data: {list(multiple_diamonds[0].keys())}")
        print(f"First diamond values: {multiple_diamonds[0]}")
    
    for i in range(0, len(multiple_diamonds), batch_size):
        batch = multiple_diamonds[i:i + batch_size]
        batch_diamonds = []
        
        for diamond_data in batch:
            try:
                # Normalize the data
                form_data = {}
                for key, value in diamond_data.items():
                    if key in ['type', 'lab', 'color', 'clarity', 'cut', 'polish', 'symmetry', 'fluorescence', 'shape']:
                        normalized_value = str(value).strip().lower()
                        if key in rawMappings:
                            mapped_value = rawMappings[key].get(normalized_value)
                            if mapped_value:
                                form_data[key] = mapped_value
                            elif key == 'shape':
                                form_data[key] = 'OT'
                            else:
                                form_data[key] = value
                        else:
                            form_data[key] = value
                    else:
                        form_data[key] = value
                
                # Get required values with proper validation
                rap_rate = form_data.get('rap_rate')
                discount_percentage = form_data.get('discount_percentage')
                carat = form_data.get('carat')
                length = form_data.get('length')
                width = form_data.get('width')
                height = form_data.get('height')
                ratio = form_data.get('ratio')
                
                # Skip diamonds with missing required fields
                if not all([rap_rate, carat, length, width, height, ratio]):
                    error_count += 1
                    print(f"Skipping diamond with missing required fields: rap_rate={rap_rate}, carat={carat}, length={length}, width={width}, height={height}, ratio={ratio}")
                    continue
                
                # Convert to proper types
                rap_rate = int(rap_rate) if rap_rate else 0
                discount_percentage = float(discount_percentage) if discount_percentage else 0
                carat = float(carat) if carat else 0
                length = float(length) if length else 0
                width = float(width) if width else 0
                height = float(height) if height else 0
                ratio = float(ratio) if ratio else 0
                
                # Calculate price_per_carat and total_amount (same as model save method)
                if discount_percentage and discount_percentage > 0:
                    price_per_carat = rap_rate - (rap_rate * discount_percentage / 100)
                else:
                    price_per_carat = rap_rate
                total_amount = carat * price_per_carat
                
                # Calculate measurements (same as model save method)
                measurements = f"{width} x {length} x {height}"
                
                # Create diamond instance without saving
                diamond = Diamond(
                    vendor=vendor,
                    type=form_data.get('type', 'CVD'),
                    stock_id=form_data.get('stock_id', ''),
                    report_number=form_data.get('report_number', 0),
                    lab=form_data.get('lab', 'IGI'),
                    shape=form_data.get('shape', 'OT'),
                    carat=carat,
                    color=form_data.get('color'),
                    clarity=form_data.get('clarity'),
                    rap_rate=rap_rate,
                    discount_percentage=discount_percentage,
                    price_per_carat=price_per_carat,
                    total_amount=total_amount,
                    cut=form_data.get('cut'),
                    polish=form_data.get('polish'),
                    symmetry=form_data.get('symmetry'),
                    fluorescence=form_data.get('fluorescence'),
                    length=length,
                    width=width,
                    height=height,
                    measurements=measurements,
                    table_percentage=form_data.get('table_percentage'),
                    depth_percentage=form_data.get('depth_percentage'),
                    crown_angle=form_data.get('crown_angle'),
                    crown_height_percentage=form_data.get('crown_height_percentage'),
                    pavilion_angle=form_data.get('pavilion_angle'),
                    pavilion_depth=form_data.get('pavilion_depth'),
                    video_360=form_data.get('video_360'),
                    photo=form_data.get('photo'),
                    pdf=form_data.get('pdf'),
                    ratio=ratio,
                    bgm=form_data.get('bgm')
                )
                
                # Basic validation
                if diamond.stock_id and diamond.report_number:
                    batch_diamonds.append(diamond)
                else:
                    error_count += 1
                    print(f"Validation failed for diamond: stock_id={diamond.stock_id}, report_number={diamond.report_number}")
                    
            except Exception as e:
                error_count += 1
                print(f"Error processing diamond: {str(e)}")
                continue
        
        # Bulk create the batch
        if batch_diamonds:
            try:
                print(f"Creating batch of {len(batch_diamonds)} diamonds...")
                # Use bulk_create with ignore_conflicts to handle duplicates
                created_diamonds = Diamond.objects.bulk_create(
                    batch_diamonds, 
                    ignore_conflicts=True,
                    batch_size=100
                )
                success_count += len(created_diamonds)
                print(f"Successfully created {len(created_diamonds)} diamonds in this batch")
            except Exception as e:
                # Log the error for debugging
                print(f"Batch error: {str(e)}")
                error_count += len(batch_diamonds)
    
    print(f"Final result: {success_count} successful, {error_count} errors")
    return success_count, error_count


def add_multiple_diamonds(request):
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Handle both form data and JSON data
            if request.content_type == 'application/json':
                try:
                    # For large JSON payloads, use streaming parser
                    if len(request.body) > 10 * 1024 * 1024:  # 10MB threshold
                        multiple_diamonds = list(ijson.items(request.body, 'multiple_diamonds'))
                    else:
                        data = json.loads(request.body)
                        multiple_diamonds = data.get('multiple_diamonds')
                except (ValueError, ImportError):
                    # Fallback to regular JSON parsing
                    data = json.loads(request.body)
                    multiple_diamonds = data.get('multiple_diamonds')
            else:
                multiple_diamonds = request.POST.get('multiple_diamonds')
                if multiple_diamonds:
                    try:
                        multiple_diamonds = json.loads(multiple_diamonds)
                    except json.JSONDecodeError:
                        messages.error(request, "Invalid JSON format in the uploaded file.")
                        return redirect('vendor:add_diamond')
            
            if multiple_diamonds:
                vendor = Vendor.objects.get(pk=request.session['user_id'])
                
                # Process diamonds with progress tracking
                total_diamonds = len(multiple_diamonds)
                
                # For very large imports, provide immediate feedback
                if total_diamonds > 1000:
                    if request.content_type == 'application/json':
                        return JsonResponse({
                            'success': True,
                            'message': f"Starting import of {total_diamonds} diamonds. This may take a few minutes.",
                            'processing': True,
                            'total_diamonds': total_diamonds
                        })
                    else:
                        messages.info(request, f"Starting import of {total_diamonds} diamonds. This may take a few minutes.")
                
                success_count, error_count = _process_multiple_diamonds_list(multiple_diamonds, vendor)

                # Return JSON response for AJAX requests
                if request.content_type == 'application/json':
                    return JsonResponse({
                        'success': success_count > 0, 
                        'success_count': success_count, 
                        'error_count': error_count,
                        'total_processed': total_diamonds,
                        'message': f"Processed {total_diamonds} diamonds: {success_count} successful, {error_count} failed."
                    })
                else:
                    # Handle form submission (fallback)
                    if success_count > 0:
                        messages.success(request, f"Successfully imported {success_count} out of {total_diamonds} diamonds.")
                    if error_count > 0:
                        messages.warning(request, f"Failed to import {error_count} out of {total_diamonds} diamonds. Please check the data format.")
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


def import_diamonds_from_api(request):
    """Fetch diamonds JSON from a provided API URL and add to logged-in vendor."""
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')

    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                api_url = data.get('api_url')
            else:
                api_url = request.POST.get('api_url')

            if not api_url:
                if request.content_type == 'application/json':
                    return JsonResponse({'success': False, 'error': 'api_url is required.'}, status=400)
                messages.error(request, 'API URL is required.')
                return redirect('vendor:add_diamond')

            # Fetch data from API with longer timeout for large datasets
            resp = requests.get(api_url, timeout=60)  # Increased timeout for large datasets
            if resp.status_code != 200:
                if request.content_type == 'application/json':
                    return JsonResponse({'success': False, 'error': f'API request failed with status {resp.status_code}.'}, status=400)
                messages.error(request, f'API request failed with status {resp.status_code}.')
                return redirect('vendor:add_diamond')

            try:
                # For large responses, use streaming JSON parser to avoid memory issues
                if len(resp.content) > 10 * 1024 * 1024:  # 10MB threshold
                    import ijson
                    payload = list(ijson.items(resp.content, ''))
                else:
                    payload = resp.json()
            except (ValueError, ImportError):
                # Fallback to regular JSON parsing
                try:
                    payload = resp.json()
                except ValueError:
                    if request.content_type == 'application/json':
                        return JsonResponse({'success': False, 'error': 'Response is not valid JSON.'}, status=400)
                    messages.error(request, 'Response is not valid JSON.')
                    return redirect('vendor:add_diamond')

            # --- Flexible extraction for variable wrappers ---
            def _looks_like_diamond(obj):
                if not isinstance(obj, dict):
                    return False
                identifier_keys = {'stock_id', 'report_number'}
                common_keys = {
                    'stock_id', 'report_number', 'carat', 'lab', 'shape', 'type',
                    'rap_rate', 'price_per_carat', 'length', 'width', 'height', 'ratio'
                }
                has_identifier = any(key in obj for key in identifier_keys)
                score = sum(1 for key in common_keys if key in obj)
                return has_identifier and score >= 2

            def _collect_diamond_dicts(node, out_list):
                # Recursively walk any JSON tree and collect dicts that look like diamonds
                if isinstance(node, list):
                    for element in node:
                        _collect_diamond_dicts(element, out_list)
                elif isinstance(node, dict):
                    # If singular object that looks like a diamond, collect it
                    if _looks_like_diamond(node):
                        out_list.append(node)
                    # Recurse into values regardless of key names (handles arbitrary wrappers)
                    for value in node.values():
                        _collect_diamond_dicts(value, out_list)

            candidates = []
            _collect_diamond_dicts(payload, candidates)

            # Prefer contiguous lists when top-level is list of dicts, but fallback to all candidates
            if isinstance(payload, list) and all(isinstance(x, dict) for x in payload):
                multiple_diamonds = payload
            else:
                multiple_diamonds = candidates

            if not multiple_diamonds:
                if request.content_type == 'application/json':
                    return JsonResponse({'success': False, 'error': 'No diamond list found in API response.'}, status=400)
                messages.error(request, 'No diamond list found in API response.')
                return redirect('vendor:add_diamond')

            vendor = Vendor.objects.get(pk=request.session['user_id'])
            
            # Process diamonds with progress tracking
            total_diamonds = len(multiple_diamonds)
            
            # For very large imports, provide immediate feedback
            if total_diamonds > 1000:
                if request.content_type == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'message': f"Starting import of {total_diamonds} diamonds. This may take a few minutes.",
                        'processing': True,
                        'total_diamonds': total_diamonds
                    })
                else:
                    messages.info(request, f"Starting import of {total_diamonds} diamonds. This may take a few minutes.")
            
            success_count, error_count = _process_multiple_diamonds_list(multiple_diamonds, vendor)

            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': success_count > 0, 
                    'success_count': success_count, 
                    'error_count': error_count,
                    'total_processed': total_diamonds,
                    'message': f"Processed {total_diamonds} diamonds: {success_count} successful, {error_count} failed."
                })

            if success_count > 0:
                messages.success(request, f"Successfully imported {success_count} out of {total_diamonds} diamonds from API.")
            if error_count > 0:
                messages.warning(request, f"Failed to import {error_count} out of {total_diamonds} diamonds from API.")
            return redirect('vendor:load_diamonds')

        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f'Error importing from API: {str(e)}')
            return redirect('vendor:add_diamond')


def view_orders(request):
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')

    vendor_id = request.session['user_id']
    orders_qs = (Order.objects.filter(vendor_id=vendor_id)
                 .order_by('-created_at')
                 .prefetch_related('items__diamond', 'customer'))

    # Mark orders as seen if they have pending items
    Order.objects.filter(
        id__in=orders_qs.values_list("id", flat=True),
        seen=False,
        items__status="Pending"
    ).update(seen=True)

    # Flatten into order_items
    order_items = []
    for order in orders_qs:
        for item in order.items.all():
            order_items.append({
                "order": order,
                "item": item,
            })

    # Paginate order_items instead of orders
    paginator = Paginator(order_items, 10)  # 10 rows per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'vendor/order.html', {'page_obj': page_obj})

def pending_orders_count(request):
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')

    vendor_id = request.session.get("user_id")

    # Count pending ORDERS (not items)
    count = Order.objects.filter(
        vendor_id=vendor_id,
        seen=False,
        items__status="Pending"
    ).distinct().count()

    return JsonResponse({"count": count})

@require_POST
def process_order_item(request, item_id):
    if request.session.get('user_type') != 'vendor' or 'user_id' not in request.session:
        return redirect('login')
    
    vendor_id = request.session.get("user_id")
    vendor = get_object_or_404(Vendor, id=vendor_id) 

    # Make sure this item belongs to one of this vendor's orders
    item = get_object_or_404(OrderItem, id=item_id, order__vendor=vendor)

    if item.status == "Pending":
        item.status = "Completed"
        item.save()
        messages.success(request, f"Item {item.diamond.stock_id} in Order #{item.order.id} marked as processed.")
    else:
        messages.info(request, f"Item {item.diamond.stock_id} is already {item.status}.")
    return redirect('vendor:view_orders')

