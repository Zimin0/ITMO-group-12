from django.urls import path
from . import views

app_name = 'mainapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    
    # Letters (3.1)
    path('letters/', views.letter_list, name='letter_list'),
    path('letters/create/', views.letter_create, name='letter_create'),
    path('letters/<int:pk>/moderate/', views.letter_moderate, name='letter_moderate'),
    
    # Warehouse (3.2)
    path('warehouse/', views.inventory_list, name='inventory_list'),
    path('warehouse/<int:item_id>/update/', views.inventory_update, name='inventory_update'),
    
    # Logistics (3.3)
    path('logistics/', views.delivery_list, name='delivery_list'),
    path('logistics/<int:pk>/status/', views.delivery_status_update, name='delivery_status_update'),
    
    # Reporting (3.2.3, 3.3.3)
    path('reports/', views.reports, name='reports'),
    path('reports/export/', views.export_pdf, name='export_pdf'),
    
    # Gifts & Categories (Reference)
    path('items/', views.ItemListView.as_view(), name='item_list'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
]
