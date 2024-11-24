from django import forms
from .models import ShippingAdress

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAdress
        fields = ['adress', 'city', 'state', 'zipcode']

        widgets = {
            'adress': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your city'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your state'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your zipcode'}),
        }
