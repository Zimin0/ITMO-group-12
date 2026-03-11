from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username



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
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        SENT = 'sent', 'Отправлено'
        APPROVED = 'approved', 'Подтверждено'
        PROCESSING = 'processing', 'В обработке'
        DELIVERED = 'delivered', 'Доставлено'

    title = models.CharField(max_length=200, verbose_name='Название подарка')
    description = models.TextField(blank=True, verbose_name='Описание')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='Статус'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='items',
        verbose_name='Категория'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='items',
        verbose_name='Автор'
    )

    class Meta:
        db_table = 'item'
        verbose_name = 'Подарок'
        verbose_name_plural = 'Подарки'
        ordering = ['-created_at']

    def __str__(self):
        return self.title