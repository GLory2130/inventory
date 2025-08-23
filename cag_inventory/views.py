from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login
from .forms import ProductForm, RegisterForm, LoginForm
from .models import Product, CustomUser, ProductConsumption
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required


def base(request):
    return render(request, 'base.html')


@login_required
def index(request):
    products = Product.objects.all().order_by('-id')  # Order by newest first
    categories = ["all"] + list(Product.objects.values_list('category', flat=True).distinct())
    selected_category = request.GET.get('category', 'all')
    search_term = request.GET.get('search', '')

    filtered_products = products.filter(
        name__icontains=search_term
    ) if selected_category == "all" else products.filter(
        name__icontains=search_term,
        category=selected_category
    )

    # Add pagination - 9 products per page
    paginator = Paginator(filtered_products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': products,
        'filtered_products': page_obj,  # Use paginated products
        'page_obj': page_obj,  # Add page object for pagination controls
        'categories': categories,
        'selected_category': selected_category,
        'search_term': search_term,
        'total_products': products.count(),
        'out_of_stock_count': products.filter(currentStock=0).count(),
        'low_stock_count': products.filter(currentStock__gt=0, currentStock__lte=F('minStock')).count(),
        'total_value': sum([p.currentStock * p.price for p in products]),
    }
    return render(request, 'index.html', context)


def home(request):
    return render(request, 'home.html')

def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        # Create user but set as inactive (requires admin approval)
        user = form.save(commit=False)
        user.is_active = False  # User cannot login until admin approves
        user.save()
        
        # Add success message indicating approval is needed
        messages.success(request, 'Registration successful! Your account is pending admin approval. You will be able to login once approved.')
        return redirect('login')
    return render(request, 'register.html', {'form': form})

@csrf_protect
def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        
        try:
            user_obj = CustomUser.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user:
                # Check if user account is active (approved by admin)
                if not user.is_active:
                    form.add_error(None, "Your account is pending admin approval. Please wait for approval before logging in.")
                else:
                    login(request, user)
                    # Redirect admin users to Django admin site
                    if user.is_staff or user.is_superuser:
                        return redirect(reverse('admin:index'))
                    else:
                        return redirect('index')
            else:
                form.add_error(None, "Invalid credentials")
        except CustomUser.DoesNotExist:
            form.add_error(None, "Invalid credentials")
    return render(request, 'login.html', {'form': form})

def logout(request):
    auth_logout(request)  # This clears the session & logs the user out
    return redirect('home')

def product_list(request):
    products = Product.objects.all()
    categories = ["all"] + list(Product.objects.values_list('category', flat=True).distinct())
    selected_category = request.GET.get('category', 'all')
    search_term = request.GET.get('search', '')

    filtered_products = products.filter(
        name__icontains=search_term
    ) if selected_category == "all" else products.filter(
        name__icontains=search_term,
        category=selected_category
    )

    form = ProductForm()
    errors = {}
    common_categories = Product.objects.values_list('category', flat=True).distinct()

    context = {
        'products': products,
        'filtered_products': filtered_products,
        'form': form,
        'errors': errors,
        'categories': categories,
        'selected_category': selected_category,
        'search_term': search_term,
        'common_categories': common_categories,
    }
    return render(request, 'products.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {'product': product}
    return render(request, 'product_detail.html', context)

def stock_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        amount_str = request.POST.get('amount', '0')
        try:
            amount = int(amount_str)
        except ValueError:
            amount = 0
        action = request.POST.get('type')
        if action == "add":
            product.currentStock += amount
        elif action == "remove" and product.currentStock >= amount:
            product.currentStock -= amount
            # Track consumption when stock is reduced
            ProductConsumption.objects.create(
                product=product,
                quantity=amount
            )
        product.save()
        return JsonResponse({'success': True, 'currentStock': product.currentStock})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def add_product(request):
    common_categories = Product.objects.values_list('category', flat=True).distinct()
    errors = {}

    if request.method == "POST":
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            if is_ajax:
                return JsonResponse({'success': True, 'product_id': product.id})
            else:
                return redirect('product_list')
        else:
            errors = form.errors
            if is_ajax:
                return JsonResponse({'success': False, 'errors': errors})
    else:
        form = ProductForm()

    # For non-AJAX GET, render the form as usual
    return render(
        request,
        'add_product_form.html',
        {
            'form': form,
            'errors': errors,
            'common_categories': common_categories,
        }
    )

def product_list_create_view(request):
    products = Product.objects.all()
    form = ProductForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('product_list')  # Replace with your URL name

    categories = ["all"] + list(Product.objects.values_list('category', flat=True).distinct())
    selected_category = request.GET.get('category', 'all')
    search_term = request.GET.get('search', '')

    filtered_products = products.filter(
        name__icontains=search_term
    ) if selected_category == "all" else products.filter(
        name__icontains=search_term,
        category=selected_category
    )

    context = {
        'products': products,
        'filtered_products': filtered_products,
        'form': form,
        'categories': categories,
        'selected_category': selected_category,
        'search_term': search_term,
    }
    return render(request, 'products.html', context)


# Product Detail, Update, Delete View
def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('product_list')

    context = {
        'product': product,
        'form': form,
    }
    return render(request, 'inventory/product_detail.html', context)


def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect('product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})


# Products In Stock View
def products_in_stock_view(request):
    products = Product.objects.filter(currentStock__gt=0)
    return render(request, 'analytics.html', {'products': products})


# Sales Analytics View
def sales_analytics_view(request):
    period = request.GET.get('period', 'daily')
    now = timezone.now()

    if period == 'daily':
        since = now - timedelta(days=1)
    elif period == 'weekly':
        since = now - timedelta(weeks=1)
    elif period == 'monthly':
        since = now - timedelta(days=30)
    else:
        since = now - timedelta(days=1)

    consumptions = (
        ProductConsumption.objects
        .filter(consumed_at__gte=since)
        .values('product__id', 'product__name')
        .annotate(total_quantity=Sum('quantity'), count=Count('id'))
        .order_by('-total_quantity')
    )

    return render(request, 'ianalytics.html', {'analytics': consumptions, 'period': period})


# Most Consumed Products View
def most_consumed_products_view(request):
    period = request.GET.get('period', 'daily')
    now = timezone.now()

    if period == 'daily':
        since = now - timedelta(days=1)
    elif period == 'weekly':
        since = now - timedelta(weeks=1)
    elif period == 'monthly':
        since = now - timedelta(days=30)
    else:
        since = now - timedelta(days=1)

    consumptions = (
        ProductConsumption.objects
        .filter(consumed_at__gte=since)
        .values('product__id', 'product__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:10]
    )

    return render(request, 'analytics.html', {'consumptions': consumptions, 'period': period})

def analytics_view(request):
    """Main analytics page that displays overview of inventory analytics"""
    products = Product.objects.all()
    
    # Get products in stock
    in_stock_products = products.filter(currentStock__gt=0)
    
    # Get most consumed products (last 30 days)
    now = timezone.now()
    since = now - timedelta(days=30)
    
    most_consumed = (
        ProductConsumption.objects
        .filter(consumed_at__gte=since)
        .values('product__id', 'product__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:10]
    )
    
    context = {
        'products': products,
        'in_stock_products': in_stock_products,
        'most_consumed': most_consumed,
    }
    return render(request, 'analytics.html', context)

def some_view(request):
    # Some logic here
    return redirect('index')  # This will redirect to the index view

@csrf_exempt
def update_product(request):
    products = Product.objects.all()
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        product.price = request.POST.get('price', product.price)
        product.currentStock = request.POST.get('currentStock', product.currentStock)
        product.minStock = request.POST.get('minStock', product.minStock)
        product.maxStock = request.POST.get('maxStock', product.maxStock)
        product.description = request.POST.get('description', product.description)
        product.save()
        return redirect('index')
    # For GET, render the form with products
    return render(request, 'update_product_form.html', {'products': products})

def real_time_analytics(request):
    """API endpoint for real-time consumption analytics"""
    from django.db.models import Sum
    from datetime import datetime, timedelta
    
    period = request.GET.get('period', 'daily')
    
    # Calculate date ranges
    now = timezone.now()
    if period == 'daily':
        start_date = now - timedelta(days=7)  
    elif period == 'weekly':
        start_date = now - timedelta(weeks=8)  
    else:  # monthly
        start_date = now - timedelta(days=365)  
    
    consumptions = ProductConsumption.objects.filter(
        consumed_at__gte=start_date
    ).values(
        'product__name'
    ).annotate(
        total_consumed=Sum('quantity')
    ).order_by('-total_consumed')[:10]  
    
    labels = [item['product__name'] for item in consumptions]
    data = [item['total_consumed'] for item in consumptions]
    
    return JsonResponse({
        'labels': labels,
        'data': data,
        'period': period
    })

def real_time_stats(request):
    """API endpoint for real-time inventory statistics"""
    from django.db.models import F
    products = Product.objects.all()
    
    stats = {
        'total_products': products.count(),
        'out_of_stock_count': products.filter(currentStock=0).count(),
        'low_stock_count': products.filter(currentStock__gt=0, currentStock__lte=F('minStock')).count(),
        'total_value': sum([p.currentStock * p.price for p in products]),
    }
    
    return JsonResponse(stats)
