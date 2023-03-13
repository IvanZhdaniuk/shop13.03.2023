# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from .models import Category, Producer, Promocode, Discount, ProductItem, RegistredUser, Basket
from .serializers import CategorySerializer, DiscountSerializer, PromocodeSerializer, \
    ProducerSerializer, ProductItemSerializer, RegistrationSerializer, LoginSerializer, BasketSerializer, \
    AddProductsSerializer, DeleteProductSerializer, OrderSerializer, ProductItemDetailSerializer
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import F


from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from .tokens import account_activation_token
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema
from .tasks import send_activation_mail, get_products_statistic


class GetStatisticView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request):
        get_products_statistic.delay()
        return Response(status=200)


class CategoriesListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowAny, )


class DiscountsListView(ListAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = (AllowAny, )


class PromocodesListView(ListAPIView):
    queryset = Promocode.objects.all()
    serializer_class = PromocodeSerializer
    permission_classes = (AllowAny, )


class ProducersListView(ListAPIView):
    queryset = Producer.objects.all()
    serializer_class = ProducerSerializer
    permission_classes = (AllowAny, )


class ProductItemsListView(ListAPIView):
    queryset = ProductItem.objects.all()
    serializer_class = ProductItemSerializer
    permission_classes = (AllowAny, )


class SingleProductItemView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, product_id):
        queryset = ProductItem.objects.prefetch_related('comment_set').filter(id=product_id).values(
            "id", "name", "description", "articul", "price", "count_on_stock", producer_name=F("producer__name"),
            category_name=F("category__name"),
            discount_name=F("discount__name"), discount_percent=F("discount__percent"),
            comment_text=F("comment__comment"), comment_author=F("comment__user__email")
        ).first()
        print(queryset)
        serializer = ProductItemDetailSerializer(queryset)
        return Response(serializer.data)


class CategoryProductsView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, cat_id):
        products = ProductItem.objects.filter(category__id=cat_id)
        serializer = ProductItemSerializer(products, many=True)
        return Response(serializer.data)


class ProducerProductView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, producer_id):
        products = ProductItem.objects.filter(producer__id=producer_id)
        serializer = ProductItemSerializer(products, many=True)
        return Response(serializer.data)


class DiscountProductsView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, discount_id):
        products = ProductItem.objects.filter(discount__id=discount_id)
        serializer = ProductItemSerializer(products, many=True)
        return Response(serializer.data)


class RegistrationView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = RegistrationSerializer

    @swagger_auto_schema(
        request_body=RegistrationSerializer,
        request_method='POST',
        responses={
            200: RegistrationSerializer
        }
    )
    def post(self, request):
        """
        create non-active account and send activation mail
        """
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        current_site = get_current_site(request)
        send_activation_mail.delay(user.id, str(current_site))

        return Response(serializer.data)


class ActivateAccountView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = RegistredUser.objects.get(id=uid)
        except Exception as e:
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response("Thank you for email confirmation!")
        return Response("Something Wrong with your account", status=403)


class LoginView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        request_body=LoginSerializer,
        request_method='POST',
        responses={
            200: LoginSerializer
        }
    )
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)


class BasketView(APIView):
    permission_classes = (IsAuthenticated, )


    @swagger_auto_schema(
        request_method='GET',
        responses={
            200: BasketSerializer
        }
    )
    def get(self, request):
        user = request.user
        basket = ProductItem.objects.prefetch_related("basket_set").filter(basket__user=user) \
            .values("name", "price", "discount", number_of_items=F("basket__number_of_items"),
                    discount_percent=F("discount__percent"), discount_expire_date=F("discount__expire_date"))
        serializer = BasketSerializer({"products": basket})

        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=AddProductsSerializer,
        request_method='POST',
        responses={
            200: "",
            409: "Not enough products on a stock"
        }
    )
    def post(self, request):
        input_serializer = AddProductsSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        product = ProductItem.objects.get(id=input_serializer.data.get('product_id'))

        if product.count_on_stock >= input_serializer.data.get('number_of_items'):
            object, created = Basket.objects.get_or_create(user=request.user, product=product)
            is_deleted = False

            if object.number_of_items:
                object.number_of_items += input_serializer.data.get('number_of_items')

                if object.number_of_items <= 0:
                    is_deleted = True
                    object.delete()
            else:
                object.number_of_items = input_serializer.data.get('number_of_items')

            if not is_deleted:
                object.save()

            return Response(status=200)

        return Response("Not enough products on a stock", status=409)


    @swagger_auto_schema(
        request_body=DeleteProductSerializer,
        request_method='DELETE',
        responses={
            200: ""
        }
    )
    def delete(self, request):
        input_serializer = DeleteProductSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        product = ProductItem.get(id=input_serializer.data.get('product_id'))
        Basket.objects.get(user=request.user, product=product).delete()

        return Response(status=200)


class CreateOrderView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=OrderSerializer,
        request_method='POST',
        responses={
            200: OrderSerializer
        }
    )
    def post(self, request):
        input_serializer = OrderSerializer(data=request.data, context={'request': request})
        input_serializer.is_valid(raise_exception=True)

        order = input_serializer.save()

        return Response(input_serializer.data)











