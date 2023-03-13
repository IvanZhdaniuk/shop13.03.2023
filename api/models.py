# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import datetime, timedelta
from django.conf import settings
import jwt


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Producer(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Discount(models.Model):
    name = models.CharField(max_length=50)
    percent = models.PositiveIntegerField()
    expire_date = models.DateTimeField()

    def __str__(self):
        return self.name


class ProductItem(models.Model):
    name = models.CharField(max_length=250)
    articul = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count_on_stock = models.PositiveIntegerField()
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    discount = models.ForeignKey(Discount, null=True, on_delete=models.SET_NULL, blank=True)

    def __str__(self):
        return self.name


class Promocode(models.Model):
    name = models.CharField(max_length=10)
    percent = models.PositiveIntegerField()
    expire_date = models.DateTimeField()
    is_allowed_to_sum_with_discounts = models.BooleanField()

    def __str__(self):
        return self.name


class Cashback(models.Model):
    name = models.CharField(max_length=15)
    percent = models.PositiveIntegerField()
    max_cashback_payment = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, password, email, phone,
                    is_admin=False, is_staff=False,
                    is_active=False, is_superuser=False,
                    age=18, login='',
                    weekly_discount_notif_required=True):

        if not phone:
            raise ValueError("User must have phone")
        if not email:
            raise ValueError("User must have email")
        if not password:
            raise ValueError("User must have password")

        user = self.model(phone=phone)
        user.set_password(password)
        user.email = email
        user.login = login
        user.age = age
        user.is_admin = is_admin
        user.is_staff = is_staff
        user.is_active = is_active
        user.is_superuser = is_superuser
        user.weekly_discount_notif_required = weekly_discount_notif_required
        user.save()

        return user


    def create_superuser(self, password, phone, email):
        if not phone:
            raise ValueError("User must have phone")
        if not email:
            raise ValueError("User must have email")
        if not password:
            raise ValueError("User must have password")

        user = self.create_user(password=password, email=email, phone=phone)
        user.is_superuser = True
        user.is_staff = True
        user.is_admin = True
        user.is_active = True
        user.weekly_discount_notif_required = False
        user.save()

        return user


class RegistredUser(AbstractUser):
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )

    username = None
    sex = models.CharField(max_length=6, choices=SEX_CHOICES, default='M')
    email = models.EmailField()
    age = models.PositiveIntegerField()
    phone = models.CharField(max_length=13, unique=True)
    login = models.CharField(max_length=200)
    weekly_discount_notif_required = models.BooleanField(default=True)
    cashback_points = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

    def __str__(self):
        return self.phone


class Basket(models.Model):
    user = models.ForeignKey(RegistredUser, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    number_of_items = models.PositiveIntegerField(default=None, null=True)


class Order(models.Model):
    DELIVERY_METHODS = (('Courier', 'Courier'),
                        ('Pickup', 'Pickup'),
                        ('Post', 'Post'))

    PAYMENT_METHODS = (('Cash', 'Cash'),
                       ('Card', 'Card'))

    PAYMENT_STATUSES = (('Paid', 'Paid'),
                        ('Waiting', 'Waiting'))

    DELIVERY_STATUSES = (('Delivered', 'Delivered'),
                         ('In process', 'In process'))

    NOTIF_TIME = ((1, 1), (6, 6), (24, 24))

    result_price = models.DecimalField(max_digits=10, decimal_places=2)
    result_number_of_items = models.PositiveIntegerField()
    product_items = models.JSONField()
    user = models.ForeignKey(RegistredUser, on_delete=models.CASCADE)
    comment = models.TextField()
    delivery_address = models.CharField(max_length=200)
    delivery_date = models.DateTimeField(null=True, blank=True)
    delivery_method = models.CharField(max_length=7, choices=DELIVERY_METHODS)
    delivery_status = models.CharField(max_length=10, choices=DELIVERY_STATUSES)
    payment_method = models.CharField(max_length=4, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=7, choices=PAYMENT_STATUSES)
    delivery_notif_required = models.BooleanField()
    delivery_notif_in_time = models.PositiveIntegerField(choices=NOTIF_TIME)
    delivery_notif_sent = models.BooleanField()


class Comment(models.Model):
    user = models.ForeignKey(RegistredUser, on_delete=models.DO_NOTHING)
    product_item = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)







