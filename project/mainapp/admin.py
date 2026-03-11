from django.contrib import admin
from .models import User, Category, Item
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'category', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('category', 'created_by')