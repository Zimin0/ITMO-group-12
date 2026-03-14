from django.db.models import Count

from .models import Category, Delivery, GiftOrder, Inventory, Item, Letter


class LetterService:
    @staticmethod
    def get_letters(status=None, child=None):
        queryset = Letter.objects.select_related('child', 'moderated_by').all()
        if status:
            queryset = queryset.filter(status=status)
        if child:
            queryset = queryset.filter(child=child)
        return queryset

    @staticmethod
    def create_letter(child, content):
        return Letter.objects.create(child=child, content=content)

    @staticmethod
    def moderate_letter(letter, status, moderator):
        letter.status = status
        letter.moderated_by = moderator
        letter.save(update_fields=['status', 'moderated_by'])
        return letter


class WarehouseService:
    @staticmethod
    def get_inventory():
        return Inventory.objects.select_related('item').all()

    @staticmethod
    def update_stock(item_id, stock):
        inventory, _ = Inventory.objects.get_or_create(item_id=item_id)
        inventory.stock = max(0, int(stock))
        inventory.save(update_fields=['stock'])
        return inventory


class LogisticsService:
    @staticmethod
    def get_deliveries(courier=None):
        queryset = Delivery.objects.select_related('order', 'courier').all()
        if courier:
            queryset = queryset.filter(courier=courier)
        return queryset


class ReportingService:
    @staticmethod
    def get_general_stats():
        return {
            'letters_total': Letter.objects.count(),
            'items_total': Item.objects.count(),
            'categories_total': Category.objects.count(),
            'orders_total': GiftOrder.objects.count(),
            'deliveries_total': Delivery.objects.count(),
            'letters_by_status': Letter.objects.values('status').annotate(total=Count('id')),
        }
