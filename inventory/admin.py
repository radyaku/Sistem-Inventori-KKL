from django.contrib import admin
from .models import Laptop, WSMCriteria, Assessment, AuditLog


@admin.register(Laptop)
class LaptopAdmin(admin.ModelAdmin):
    list_display = ('asset_code', 'brand', 'model', 'status', 'physical_grade', 'last_user', 'created_at')
    list_filter = ('status', 'brand', 'physical_grade', 'storage_type')
    search_fields = ('asset_code', 'serial_number', 'brand', 'model', 'last_user')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Identifikasi', {
            'fields': ('asset_code', 'serial_number')
        }),
        ('Spesifikasi', {
            'fields': ('brand', 'model', 'processor', 'ram_gb', 'storage_type', 'storage_size_gb', 'gpu')
        }),
        ('Status', {
            'fields': ('status', 'physical_grade', 'last_user')
        }),
        ('Finansial', {
            'fields': ('open_price', 'sold_price', 'buyer_name')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WSMCriteria)
class WSMCriteriaAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'weight', 'attribute_type', 'is_active')
    list_filter = ('attribute_type', 'is_active')
    ordering = ('code',)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('laptop', 'wsm_score', 'final_grade', 'assessed_at', 'assessed_by')
    list_filter = ('final_grade', 'assessed_at')
    search_fields = ('laptop__asset_code', 'laptop__brand', 'laptop__model')
    readonly_fields = ('wsm_score', 'final_grade', 'assessed_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'model_name', 'object_repr')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'object_repr')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'timestamp')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
