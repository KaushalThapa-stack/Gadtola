from django.db import models
from store.models import Product, Variation

# Session-based cart system (no user authentication)


class Cart(models.Model):
    """
    Session-based shopping cart.
    No user FK - identified by session ID only.
    """
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    """
    Individual items in cart.
    Linked to cart by session ID, not by user.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __unicode__(self):
        return str(self.product)

