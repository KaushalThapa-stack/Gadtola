from django import forms
from .models import Order



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone','email','address_line_1','address_line_2','state','city','order_note']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError('Enter a 10-digit phone number')
        return phone
