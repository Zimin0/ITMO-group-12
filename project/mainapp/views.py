from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils import timezone
from django.db.models import Count

from .models import Item, Category, User, Letter, GiftOrder, Inventory, Delivery
from .forms import (
    ItemForm, CategoryForm, UserRegistrationForm, LetterForm, 
    OrderStatusForm, InventoryForm, DeliveryForm
)
from .services import (
    LetterService, WarehouseService, LogisticsService, ReportingService
)

# Access Control Helpers
def role_required(*roles):
    return user_passes_test(lambda u: u.is_authenticated and (u.role in roles or u.is_staff or u.is_superuser))

# --- Auth & Registration ---
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # If user is superuser or staff, ensure they don't have Role.CHILD by default if they were created differently
            # But for regular registration, they get Role.CHILD.
            login(request, user)
            messages.success(request, f"Регистрация успешна! Добро пожаловать, {user.username}!")
            return redirect('mainapp:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def home(request):
    stats = ReportingService.get_general_stats()
    return render(request, 'home.html', {'stats': stats})

# --- Letter System (Child & Helper) ---
@login_required
def letter_list(request):
    # Дети видят только свои письма, помощники и админы видят все
    if request.user.is_superuser or request.user.is_staff:
        status = request.GET.get('status')
        letters = LetterService.get_letters(status=status)
    elif request.user.role == User.Role.CHILD:
        letters = LetterService.get_letters(child=request.user)
    elif request.user.role in [User.Role.HELPER]:
        status = request.GET.get('status')
        letters = LetterService.get_letters(status=status)
    else:
        messages.error(request, "Доступ запрещен.")
        return redirect('mainapp:home')
    
    return render(request, 'letters/letter_list.html', {'letters': letters})

@login_required
@role_required(User.Role.CHILD)
def letter_create(request):
    if request.method == 'POST':
        form = LetterForm(request.POST)
        if form.is_valid():
            LetterService.create_letter(request.user, form.cleaned_data['content'])
            messages.success(request, "Письмо успешно отправлено Дедушке Морозу!")
            return redirect('mainapp:letter_list')
    else:
        form = LetterForm()
    return render(request, 'letters/letter_form.html', {'form': form, 'title': 'Написать письмо'})

@login_required
@role_required(User.Role.HELPER, User.Role.ADMIN)
def letter_moderate(request, pk):
    letter = get_object_or_404(Letter, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in [Letter.Status.APPROVED, Letter.Status.REJECTED]:
            LetterService.moderate_letter(letter, status, request.user)
            messages.success(request, f"Письмо #{letter.id} обновлено: {letter.get_status_display()}")
            return redirect('mainapp:letter_list')
    return render(request, 'letters/letter_detail.html', {'letter': letter})

# --- Warehouse System ---
@login_required
@role_required(User.Role.WAREHOUSE, User.Role.ADMIN)
def inventory_list(request):
    inventory = WarehouseService.get_inventory()
    items = Item.objects.all()
    return render(request, 'warehouse/inventory.html', {'inventory': inventory, 'items': items})

@login_required
@role_required(User.Role.WAREHOUSE, User.Role.ADMIN)
def inventory_update(request, item_id):
    if request.method == 'POST':
        stock = request.POST.get('stock')
        WarehouseService.update_stock(item_id, stock)
        messages.success(request, "Запасы обновлены.")
    return redirect('mainapp:inventory_list')

# --- Logistics System ---
@login_required
@role_required(User.Role.COURIER, User.Role.ADMIN, User.Role.HELPER)
def delivery_list(request):
    if request.user.role == User.Role.COURIER:
        deliveries = LogisticsService.get_deliveries(courier=request.user)
    else:
        deliveries = LogisticsService.get_deliveries()
    return render(request, 'logistics/delivery_list.html', {'deliveries': deliveries})

@login_required
@role_required(User.Role.COURIER, User.Role.ADMIN)
def delivery_status_update(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        delivery.status = status
        if status == Delivery.Status.DELIVERED:
            from django.utils import timezone
            delivery.delivered_at = timezone.now()
        delivery.save()
        messages.success(request, f"Статус доставки #{delivery.id} изменен.")
    return redirect('mainapp:delivery_list')

# --- Reporting ---
@login_required
@role_required(User.Role.ADMIN, User.Role.CHARITY, User.Role.HELPER)
def reports(request):
    stats = ReportingService.get_general_stats()
    # Статистика по категориям
    category_stats = Category.objects.annotate(item_count=Count('items')).all()
    return render(request, 'reports/dashboard.html', {'stats': stats, 'category_stats': category_stats})

@login_required
@role_required(User.Role.ADMIN, User.Role.CHARITY, User.Role.HELPER)
def export_pdf(request):
    template_path = 'reports/report_pdf.html'
    stats = ReportingService.get_general_stats()
    category_stats = Category.objects.annotate(item_count=Count('items')).all()
    
    context = {
        'stats': stats,
        'category_stats': category_stats,
        'date': timezone.now()
    }
    
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="santa_report.pdf"'
    
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    
    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# --- Gifts & Categories (CRUD) ---
class ItemListView(ListView):
    model = Item
    template_name = 'items/item_list.html'
    context_object_name = 'items'

class CategoryListView(ListView):
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'
