from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .models import Laptop, Assessment, WSMCriteria, AuditLog
from .forms import LaptopForm, AssessmentForm, WSMCriteriaForm, StatusChangeForm
from .services.wsm_calculator import process_assessment, get_grade_recommendation


def create_audit_log(user, action, instance, changes=None):
    """Helper untuk membuat audit log"""
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance),
        changes=changes
    )


# ============================================
# LAPTOP CRUD VIEWS
# ============================================

@login_required
def laptop_list(request):
    """Halaman Daftar Seluruh Aset (Master Data Aset)"""
    laptops = Laptop.objects.select_related('assessment').all()
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        laptops = laptops.filter(
            Q(asset_code__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(last_user__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        laptops = laptops.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(laptops, 10)
    page = request.GET.get('page', 1)
    laptops_page = paginator.get_page(page)
    
    context = {
        'laptops': laptops_page,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Laptop.STATUS_CHOICES,
    }
    return render(request, 'inventory/laptop_list.html', context)


@login_required
def laptop_create(request):
    """Form tambah aset baru"""
    if request.method == 'POST':
        form = LaptopForm(request.POST)
        if form.is_valid():
            laptop = form.save()
            create_audit_log(request.user, 'create', laptop)
            messages.success(request, f'Aset {laptop.asset_code} berhasil ditambahkan!')
            return redirect('inventory:laptop_list')
    else:
        form = LaptopForm()
    
    context = {'form': form, 'title': 'Tambah Aset Baru'}
    return render(request, 'inventory/laptop_form.html', context)


@login_required
def laptop_detail(request, pk):
    """Detail aset"""
    laptop = get_object_or_404(Laptop, pk=pk)
    assessment = getattr(laptop, 'assessment', None)
    recommendation = None
    
    if assessment and assessment.final_grade:
        recommendation = get_grade_recommendation(assessment.final_grade)
    
    context = {
        'laptop': laptop,
        'assessment': assessment,
        'recommendation': recommendation,
    }
    return render(request, 'inventory/laptop_detail.html', context)


@login_required
def laptop_edit(request, pk):
    """Form edit aset"""
    laptop = get_object_or_404(Laptop, pk=pk)
    
    if request.method == 'POST':
        form = LaptopForm(request.POST, instance=laptop)
        if form.is_valid():
            laptop = form.save()
            create_audit_log(request.user, 'update', laptop)
            messages.success(request, f'Aset {laptop.asset_code} berhasil diperbarui!')
            return redirect('inventory:laptop_list')
    else:
        form = LaptopForm(instance=laptop)
    
    context = {'form': form, 'title': f'Edit Aset {laptop.asset_code}', 'laptop': laptop}
    return render(request, 'inventory/laptop_form.html', context)


@login_required
def laptop_delete(request, pk):
    """Hapus aset"""
    laptop = get_object_or_404(Laptop, pk=pk)
    
    if request.method == 'POST':
        asset_code = laptop.asset_code
        create_audit_log(request.user, 'delete', laptop)
        laptop.delete()
        messages.success(request, f'Aset {asset_code} berhasil dihapus!')
        return redirect('inventory:laptop_list')
    
    context = {'laptop': laptop}
    return render(request, 'inventory/laptop_confirm_delete.html', context)


@login_required
def laptop_change_status(request, pk):
    """Ubah status aset"""
    laptop = get_object_or_404(Laptop, pk=pk)
    
    if request.method == 'POST':
        form = StatusChangeForm(request.POST)
        if form.is_valid():
            old_status = laptop.status
            new_status = form.cleaned_data['new_status']
            
            laptop.status = new_status
            
            if new_status == 'sold':
                laptop.sold_price = form.cleaned_data['sold_price']
                laptop.buyer_name = form.cleaned_data['buyer_name']
            
            laptop.save()
            
            create_audit_log(
                request.user, 
                'status_change', 
                laptop,
                {'old_status': old_status, 'new_status': new_status}
            )
            
            messages.success(request, f'Status aset {laptop.asset_code} berhasil diubah ke {laptop.get_status_display()}!')
            return redirect('inventory:laptop_detail', pk=pk)
    else:
        form = StatusChangeForm()
    
    context = {'form': form, 'laptop': laptop}
    return render(request, 'inventory/laptop_change_status.html', context)


# ============================================
# WSM ASSESSMENT VIEWS
# ============================================

@login_required
def assessment_list(request):
    """Daftar assessment"""
    assessments = Assessment.objects.select_related('laptop').order_by('-assessed_at')
    
    paginator = Paginator(assessments, 10)
    page = request.GET.get('page', 1)
    assessments_page = paginator.get_page(page)
    
    context = {'assessments': assessments_page}
    return render(request, 'inventory/assessment_list.html', context)


@login_required
def assessment_input(request):
    """Input Penilaian WSM Untuk Aset"""
    # Get list of laptops for autocomplete
    laptops = Laptop.objects.filter(status__in=['draft', 'assessed']).values('asset_code', 'brand', 'model')
    
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        laptop_code = request.POST.get('laptop_code', '')
        
        try:
            laptop = Laptop.objects.get(asset_code=laptop_code)
        except Laptop.DoesNotExist:
            messages.error(request, f'Kode aset {laptop_code} tidak ditemukan!')
            return redirect('inventory:assessment_input')
        
        if form.is_valid():
            # Check if assessment already exists
            assessment, created = Assessment.objects.get_or_create(
                laptop=laptop,
                defaults={
                    'screen_condition': form.cleaned_data['screen_condition'],
                    'physical_condition': form.cleaned_data['physical_condition'],
                    'battery_health': form.cleaned_data['battery_health'],
                    'keyboard_status': form.cleaned_data['keyboard_status'],
                    'touchpad_status': form.cleaned_data['touchpad_status'],
                    'specs_score': form.cleaned_data['specs_score'],
                    'power_status': form.cleaned_data['power_status'],
                    'connectivity_score': form.cleaned_data['connectivity_score'],
                    'camera_ok': form.cleaned_data['camera_ok'],
                    'speaker_ok': form.cleaned_data['speaker_ok'],
                    'usb_port_ok': form.cleaned_data['usb_port_ok'],
                    'hinge_broken': form.cleaned_data['hinge_broken'],
                    'screw_missing': form.cleaned_data['screw_missing'],
                    'dent_crack': form.cleaned_data['dent_crack'],
                    'condition_notes': form.cleaned_data['condition_notes'],
                    'assessed_by': request.user,
                }
            )
            
            if not created:
                # Update existing assessment
                for field in form.cleaned_data:
                    if field != 'laptop_code':
                        setattr(assessment, field, form.cleaned_data[field])
                assessment.assessed_by = request.user
            
            # Calculate WSM score
            assessment = process_assessment(assessment, save=True)
            
            create_audit_log(request.user, 'assess', laptop)
            
            messages.success(
                request, 
                f'Penilaian untuk {laptop.asset_code} berhasil! Skor WSM: {assessment.wsm_score}, Grade: {assessment.final_grade}'
            )
            return redirect('inventory:grading_results')
    else:
        form = AssessmentForm()
    
    context = {
        'form': form,
        'laptops': list(laptops),
    }
    return render(request, 'inventory/assessment_input.html', context)


@login_required
def assessment_detail(request, pk):
    """Detail assessment"""
    assessment = get_object_or_404(Assessment, pk=pk)
    recommendation = get_grade_recommendation(assessment.final_grade)
    
    context = {
        'assessment': assessment,
        'recommendation': recommendation,
    }
    return render(request, 'inventory/assessment_detail.html', context)


# ============================================
# GRADING RESULTS VIEW
# ============================================

@login_required
def grading_results(request):
    """Hasil Grading Aset"""
    assessments = Assessment.objects.select_related('laptop').order_by('-assessed_at')
    
    # Filter by grade
    grade_filter = request.GET.get('grade', '')
    if grade_filter:
        assessments = assessments.filter(final_grade=grade_filter)
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        assessments = assessments.filter(
            Q(laptop__asset_code__icontains=search_query) |
            Q(laptop__serial_number__icontains=search_query) |
            Q(laptop__brand__icontains=search_query) |
            Q(laptop__model__icontains=search_query)
        )
    
    # Stats
    total = Assessment.objects.count()
    grade_a_count = Assessment.objects.filter(final_grade='A').count()
    grade_b_count = Assessment.objects.filter(final_grade='B').count()
    grade_c_count = Assessment.objects.filter(final_grade='C').count()
    grade_d_count = Assessment.objects.filter(final_grade='D').count()
    
    context = {
        'assessments': assessments,
        'grade_filter': grade_filter,
        'search_query': search_query,
        'total': total,
        'grade_a_count': grade_a_count,
        'grade_b_count': grade_b_count,
        'grade_c_count': grade_c_count,
        'grade_d_count': grade_d_count,
    }
    return render(request, 'inventory/grading_results.html', context)


# ============================================
# AUDIT LOG VIEW
# ============================================

@login_required
def audit_log(request):
    """Log Audit"""
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')
    
    # Filter by action
    action_filter = request.GET.get('action', '')
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    paginator = Paginator(logs, 20)
    page = request.GET.get('page', 1)
    logs_page = paginator.get_page(page)
    
    context = {
        'logs': logs_page,
        'action_filter': action_filter,
        'action_choices': AuditLog.ACTION_CHOICES,
    }
    return render(request, 'inventory/audit_log.html', context)


# ============================================
# SETTINGS VIEWS
# ============================================

@login_required
def settings_view(request):
    """Halaman Settings"""
    context = {}
    return render(request, 'inventory/settings.html', context)


@login_required
def criteria_list(request):
    """Daftar kriteria WSM"""
    criteria = WSMCriteria.objects.all()
    total_weight = sum(c.weight for c in criteria)
    
    context = {
        'criteria': criteria,
        'total_weight': total_weight,
    }
    return render(request, 'inventory/criteria_list.html', context)


@login_required
def criteria_create(request):
    """Form tambah kriteria"""
    if request.method == 'POST':
        form = WSMCriteriaForm(request.POST)
        if form.is_valid():
            criteria = form.save()
            messages.success(request, f'Kriteria {criteria.code} berhasil ditambahkan!')
            return redirect('inventory:criteria_list')
    else:
        form = WSMCriteriaForm()
    
    context = {'form': form, 'title': 'Tambah Kriteria WSM'}
    return render(request, 'inventory/criteria_form.html', context)


@login_required
def criteria_edit(request, pk):
    """Form edit kriteria"""
    criteria = get_object_or_404(WSMCriteria, pk=pk)
    
    if request.method == 'POST':
        form = WSMCriteriaForm(request.POST, instance=criteria)
        if form.is_valid():
            criteria = form.save()
            messages.success(request, f'Kriteria {criteria.code} berhasil diperbarui!')
            return redirect('inventory:criteria_list')
    else:
        form = WSMCriteriaForm(instance=criteria)
    
    context = {'form': form, 'title': f'Edit Kriteria {criteria.code}', 'criteria': criteria}
    return render(request, 'inventory/criteria_form.html', context)
