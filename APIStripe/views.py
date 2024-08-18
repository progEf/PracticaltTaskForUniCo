from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
import stripe
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from APIStripe.models import Item

# Create your views here.
#
stripe.api_key = 'sk_test_51PogkZDqoX7B4MqDqzVQqqfsY5dC6eUDaEEf7yNjGvgGQKGMmmycB11IWKwfAAQhycizCo9DNYUchTd5Lbri11em00UwEW1y6S'


class AllProducts(APIView):# page/
    def get(self, request):
        paginator = PageNumberPagination()# Создаем экземпляр пагинатора
        paginator.page_size = 9  #  размер страницы
        items = Item.objects.values('id', 'name', 'price')  #выбираем  необходимые поля
        paginated_items = paginator.paginate_queryset(items, request) # Пагинируем запрос, используя переданные параметры из запроса

        return paginator.get_paginated_response(paginated_items)


def products_home(request): # home page
    return render(request, 'home.html', )


class BuyView(APIView):  # GET /buy/{id}:
    def get(self, request, id):
        host = request.get_host()

        try:
            # Получение товара по идентификатору
            product = Item.objects.get(id=id)

            # Создание сессии оформления заказа
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': product.name,
                            },
                            'unit_amount': int(product.price * 100),
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=f'http://{host}/',
                cancel_url=f'http://{host}/',
            )

            return JsonResponse({'sessionId': session.id})
        except Item.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def item_detail(request, id): #
    item = get_object_or_404(Item, id=id) # Пытаемся получить объект Item по указанному id; если не найден, возвращаем 404
    return render(request, 'product.html', {'item': item})
