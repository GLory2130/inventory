from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Product, ProductConsumption

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'currentStock', 'price', 'category', 'lastUpdated']
    list_filter = ['category', 'lastUpdated']
    search_fields = ['name', 'description']
    list_editable = ['currentStock', 'price']
    readonly_fields = ['lastUpdated']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'category', 'supplier')
        }),
        ('Inventory Details', {
            'fields': ('currentStock', 'minStock', 'maxStock', 'price')
        }),
        ('Timestamps', {
            'fields': ('lastUpdated',),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductConsumption)
class ProductConsumptionAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'consumed_at']
    list_filter = ['consumed_at', 'product__category']
    search_fields = ['product__name']
    readonly_fields = []
    
    fieldsets = (
        ('Consumption Details', {
            'fields': ('product', 'quantity')
        }),
        ('Additional Information', {
            'fields': ('consumed_at',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')
