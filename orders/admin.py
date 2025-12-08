from django.contrib import admin
from .models import Order,OrderProduct

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('user', 'product' , 'quantity' , 'product_price' , 'ordered', 'phone')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number','full_name','email','phone','city','order_total','tax','status','is_ordered','created_at')
    list_filter = ('status','is_ordered')
    search_fields = ('order_number','first_name','last_name','email','phone')
    list_per_page = 20
    actions = ['mark_ordered', 'mark_completed']
    inlines = [OrderProductInline]

    def mark_ordered(self, request, queryset):
        queryset.update(status='Accepted')
    mark_ordered.short_description = 'Move selected to Ordered'

    def mark_completed(self, request, queryset):
        queryset.update(status='Completed')
    mark_completed.short_description = 'Move selected to Completed'


admin.site.register(Order,OrderAdmin)

class DeliveryStatusFilter(admin.SimpleListFilter):
    title = 'delivery status'
    parameter_name = 'delivery_status'

    def lookups(self, request, model_admin):
        return (
            ('ordered', 'Ordered'),
            ('completed', 'Completed'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'ordered':
            return queryset.filter(order__status__in=['New','Accepted'])
        if value == 'completed':
            return queryset.filter(order__status='Completed')
        return queryset


class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order','product','quantity','product_price','ordered','phone','order_status','delivery_status','created_at')
    list_filter = ('ordered','order__status', DeliveryStatusFilter)
    list_editable = ('ordered',)

    def order_status(self, obj):
        return obj.order.status

    def delivery_status(self, obj):
        return 'Completed' if obj.order.status == 'Completed' else 'Ordered'

admin.site.register(OrderProduct, OrderProductAdmin)
