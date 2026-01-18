from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from inventory.models import Laptop, Assessment


def login_view(request):
    """Halaman login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Selamat datang, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Username atau password salah.')
    
    return render(request, 'core/login.html')


def logout_view(request):
    """Logout dan redirect ke login"""
    logout(request)
    messages.info(request, 'Anda telah keluar dari sistem.')
    return redirect('login')


@login_required
def dashboard(request):
    """Halaman utama - Dashboard dengan statistik"""
    # Get statistics
    total_assets = Laptop.objects.count()
    assets_ready = Laptop.objects.filter(status='ready').count()
    assets_sold = Laptop.objects.filter(status='sold').count()
    assets_draft = Laptop.objects.filter(status='draft').count()
    
    # Calculate revenue
    from django.db.models import Sum
    revenue = Laptop.objects.filter(status='sold').aggregate(
        total=Sum('sold_price')
    )['total'] or 0
    
    # Get grade distribution
    grade_a = Assessment.objects.filter(final_grade='A').count()
    grade_b = Assessment.objects.filter(final_grade='B').count()
    grade_c = Assessment.objects.filter(final_grade='C').count()
    grade_d = Assessment.objects.filter(final_grade='D').count()
    
    # Recent assets
    recent_assets = Laptop.objects.order_by('-created_at')[:5]
    
    context = {
        'total_assets': total_assets,
        'assets_ready': assets_ready,
        'assets_sold': assets_sold,
        'assets_draft': assets_draft,
        'revenue': revenue,
        'grade_a': grade_a,
        'grade_b': grade_b,
        'grade_c': grade_c,
        'grade_d': grade_d,
        'recent_assets': recent_assets,
    }
    
    return render(request, 'core/dashboard.html', context)
