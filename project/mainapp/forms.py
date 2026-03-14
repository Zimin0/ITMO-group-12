from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Item, Category, User, Letter, GiftOrder, Inventory, Delivery

class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'phone', 'address')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude 'admin' role from registration form
        self.fields['role'].choices = [
            choice for choice in User.Role.choices if choice[0] != User.Role.ADMIN
        ]
        # Add form-input class to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'category', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название подарка'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-input'}),
        }

class LetterForm(forms.ModelForm):
    class Meta:
        model = Letter
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': 'Дорогой Дедушка Мороз...'}),
        }

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = GiftOrder
        fields = ['status']
        widgets = {'status': forms.Select(attrs={'class': 'form-input'})}

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['stock']
        widgets = {'stock': forms.NumberInput(attrs={'class': 'form-input'})}

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['courier', 'status']
        widgets = {
            'courier': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название категории'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }
