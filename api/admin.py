# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Category, Cashback, ProductItem, \
    Producer, Promocode, RegistredUser, Discount, Order, Basket, Comment


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', ]


class PromocodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'percent',
                    'is_allowed_to_sum_with_discounts',
                    'expire_date']
    search_fields = ['name', ]


class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'percent', 'expire_date']
    search_fields = ['name', ]


class ProductItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'articul', 'price', 'category',
                    'producer', 'count_on_stock']
    search_fields = ['name', 'category__name', 'articul', 'producer__name']


class ProducerAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    search_fields = ['name', ]


class CashbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'percent', 'max_cashback_payment']


class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.get_fields()]
    search_fields = ['user__phone', 'user__email']


class RegistredUserAdmin(admin.ModelAdmin):
    list_display = ['phone', 'email', 'login', 'is_active', 'cashback_points']
    search_fields = ['phone', 'email', 'login']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['comment', 'created_at', 'get_user', 'get_product_item']

    @admin.display(ordering='user__email', description='User')
    def get_user(self, obj):
        return obj.user.email

    @admin.display(ordering='product_item__name', description='ProductItem')
    def get_product_item(self, obj):
        return obj.product_item.name


admin.site.register(Category, CategoryAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(ProductItem, ProductItemAdmin)
admin.site.register(Promocode, PromocodeAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Cashback, CashbackAdmin)
admin.site.register(Producer, ProducerAdmin)
admin.site.register(RegistredUser, RegistredUserAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Basket)






