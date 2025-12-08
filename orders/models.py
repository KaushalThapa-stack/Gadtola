from django.db import models
from accounts.models import Account
from store.models import Product, Variation
import secrets
import string

class Order(models.Model):
    STATUS = (
        ('New','New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    order_number= models.CharField(max_length=20)
    tracking_id = models.CharField(max_length=10, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    secure_token = models.CharField(max_length=64, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True)


    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def generate_secure_token(self):
        """Generate a unique secure token for the order"""
        return secrets.token_urlsafe(32)
    
    def generate_tracking_id(self):
        """Generate a unique 10-character tracking ID"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(10))

    def save(self, *args, **kwargs):
        """Override save to generate secure token and tracking ID if not exists"""
        if not self.secure_token:
            self.secure_token = self.generate_secure_token()
        if not self.tracking_id:
            self.tracking_id = self.generate_tracking_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation,blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    phone = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.product.product_name
