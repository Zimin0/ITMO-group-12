from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        CHILD = 'child', 'Ребенок'
        HELPER = 'helper', 'Помощник Деда Мороза'
        COURIER = 'courier', 'Курьер'
        WAREHOUSE = 'warehouse', 'Складская служба'
        CHARITY = 'charity', 'Благотворительная организация'
        ADMIN = 'admin', 'Администратор'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CHILD,
        verbose_name='Роль'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    address = models.TextField(blank=True, verbose_name='Адрес')

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        db_table = 'category'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

class Item(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название подарка')
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='items',
        verbose_name='Категория'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Условная стоимость')

    class Meta:
        db_table = 'item'
        verbose_name = 'Подарок (тип)'
        verbose_name_plural = 'Подарки (типы)'

    def __str__(self):
        return self.title

class Inventory(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='inventory')
    stock = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    reserved = models.PositiveIntegerField(default=0, verbose_name='Зарезервировано')

    class Meta:
        verbose_name = 'Складской запас'
        verbose_name_plural = 'Складские запасы'

class Letter(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новое'
        APPROVED = 'approved', 'Подтверждено'
        REJECTED = 'rejected', 'Отклонено'
        PROCESSING = 'processing', 'В обработке'
        COMPLETED = 'completed', 'Выполнено'

    child = models.ForeignKey(User, on_delete=models.CASCADE, related_name='letters', verbose_name='Ребенок')
    content = models.TextField(verbose_name='Текст письма')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата получения')
    moderated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='moderated_letters', verbose_name='Проверено помощником'
    )

    class Meta:
        verbose_name = 'Письмо'
        verbose_name_plural = 'Письма'
        ordering = ['-created_at']

class GiftOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает сборки'
        PACKING = 'packing', 'Комплектуется'
        READY = 'ready', 'Готов к отправке'
        SHIPPED = 'shipped', 'Передан курьеру'
        DELIVERED = 'delivered', 'Доставлен'
        CANCELLED = 'cancelled', 'Отменен'

    letter = models.OneToOneField(Letter, on_delete=models.CASCADE, related_name='order', verbose_name='Письмо')
    items = models.ManyToManyField(Item, related_name='orders', verbose_name='Подарки в заказе')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус заказа'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ подарков'
        verbose_name_plural = 'Заказы подарков'

class Delivery(models.Model):
    class Status(models.TextChoices):
        ASSIGNED = 'assigned', 'Назначен курьер'
        IN_TRANSIT = 'in_transit', 'В пути'
        DELIVERED = 'delivered', 'Доставлено'
        FAILED = 'failed', 'Не удалось доставить'

    order = models.OneToOneField(GiftOrder, on_delete=models.CASCADE, related_name='delivery', verbose_name='Заказ')
    courier = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, 
        related_name='deliveries', verbose_name='Курьер'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ASSIGNED,
        verbose_name='Статус доставки'
    )
    route_data = models.JSONField(null=True, blank=True, verbose_name='Данные маршрута (JSON)')
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Доставка'
        verbose_name_plural = 'Доставки'
