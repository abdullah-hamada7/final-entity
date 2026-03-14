# orders/urls.py
from django.urls import path
from . import views, api_views
from offers.views import add_all_offer_products

app_name = 'orders'

urlpatterns = [
    # صفحات HTML التقليدية
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='list'),
    path('orders/<str:order_number>/', views.order_detail, name='detail'),
    path('cart/add-all/<int:offer_id>/', views.add_all_offer_products, name='add_all_offer_products'),

    # REST API Endpoints
    path("submit-cart/", views.submit_cart, name="submit_cart"),
    path('api/cart/', api_views.CartAPIView.as_view(), name='api_cart'),
    path('api/cart/add/', api_views.AddToCartAPIView.as_view(), name='api_add_to_cart'),
    path('api/cart/update/', api_views.UpdateCartQuantityAPIView.as_view(), name='api_update_quantity'),
    path('api/cart/remove/', api_views.RemoveFromCartAPIView.as_view(), name='api_remove_from_cart'),
    path('api/cart/clear/', api_views.ClearCartAPIView.as_view(), name='api_clear_cart'),
    path('api/orders/create/', api_views.CreateOrderAPIView.as_view(), name='api_create_order'),
    path('api/orders/', api_views.OrderListAPIView.as_view(), name='api_order_list'),
    path('api/orders/<str:order_number>/', api_views.OrderDetailAPIView.as_view(), name='api_order_detail'),
]