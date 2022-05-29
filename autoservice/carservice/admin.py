from django.contrib import admin
from .models import CarModel, Car, Order, OrderLine, Service, Profile


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0
    can_delete = False
    

class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineInline, )
    list_display = ('car', 'owner', 'date', 'due_back', 'display_services', 'status')

    fieldsets = (
        (None, {
            'fields': ('status', 'car', )
        }),
        ('Uzsakymo informacija', {
            'fields': ( 'date', 'due_back', 'owner', 'sum_total')
        }),
                )


class CarAdmin(admin.ModelAdmin):
    list_display = ('plate_nr', 'car_model', 'vin_code', 'client', )
    list_filter = ('client', 'car_model')
    search_fields = ('plate_nr', 'vin_code', 'car_model__year')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')




admin.site.register(CarModel)
admin.site.register(Car, CarAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLine)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Profile)

