from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mainapp.urls')),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('items/', TemplateView.as_view(template_name='items_stub.html'), name='items'),
    path('categories/', TemplateView.as_view(template_name='categories_stub.html'), name='categories'),
]