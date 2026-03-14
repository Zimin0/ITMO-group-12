from django.contrib import admin
from .models import User, Category, Item, Inventory, Letter, GiftOrder, Delivery

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'email', 'is_staff')
    list_filter = ('role', 'is_staff')
    search_fields = ('username', 'email')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('title', 'description')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('item', 'stock', 'reserved')

@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ('child', 'status', 'created_at', 'moderated_by')
    list_filter = ('status', 'created_at')
    search_fields = ('content', 'child__username')

@admin.register(GiftOrder)
class GiftOrderAdmin(admin.ModelAdmin):
    list_display = ('letter', 'status', 'updated_at')
    list_filter = ('status',)

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'courier', 'status', 'delivered_at')
    list_filter = ('status', 'delivered_at')
