from django.db.models import Q, Count, Sum
from django.utils import timezone
from .models import Item, Category, Letter, GiftOrder, Inventory, Delivery, User

class LetterService:
    @staticmethod
    def get_letters(status=None, child=None):
        letters = Letter.objects.select_related('child', 'moderated_by').all()
        if status:
            letters = letters.filter(status=status)
        if child:
            letters = letters.filter(child=child)
        return letters

    @staticmethod
    def create_letter(child, content):
        return Letter.objects.create(child=child, content=content)

    @staticmethod
    def moderate_letter(letter, status, helper):
        letter.status = status
        letter.moderated_by = helper
        letter.save()
        
        # Если письмо одобрено, создаем заказ
        if status == Letter.Status.APPROVED:
            GiftOrder.objects.get_or_create(letter=letter)
        return letter

class WarehouseService:
    @staticmethod
    def get_inventory():
        return Inventory.objects.select_related('item', 'item__category').all()

    @staticmethod
    def update_stock(item_id, quantity):
        inventory, _ = Inventory.objects.get_or_create(item_id=item_id)
        inventory.stock = quantity
        inventory.save()
        return inventory

    @staticmethod
    def pack_order(order, item_ids):
        # Логика комплектации: проверка наличия и списание
        items = Item.objects.filter(id__in=item_ids)
        for item in items:
            inventory = getattr(item, 'inventory', None)
            if inventory and inventory.stock > 0:
                inventory.stock -= 1
                inventory.save()
            else:
                # В реальной системе тут была бы ошибка "Нет в наличии"
                pass
        
        order.items.set(items)
        order.status = GiftOrder.Status.PACKING
        order.save()
        return order

class LogisticsService:
    @staticmethod
    def get_deliveries(courier=None, status=None):
        deliveries = Delivery.objects.select_related('order', 'courier', 'order__letter').all()
        if courier:
            deliveries = deliveries.filter(courier=courier)
        if status:
            deliveries = deliveries.filter(status=status)
        return deliveries

    @staticmethod
    def assign_delivery(order, courier):
        delivery, _ = Delivery.objects.get_or_create(order=order)
        delivery.courier = courier
        delivery.status = Delivery.Status.ASSIGNED
        delivery.save()
        
        order.status = GiftOrder.Status.SHIPPED
        order.save()
        return delivery

class ReportingService:
    @staticmethod
    def get_general_stats():
        return {
            'total_letters': Letter.objects.count(),
            'approved_letters': Letter.objects.filter(status=Letter.Status.APPROVED).count(),
            'delivered_gifts': Delivery.objects.filter(status=Delivery.Status.DELIVERED).count(),
            'warehouse_stock': Inventory.objects.aggregate(total=Sum('stock'))['total'] or 0
        }
