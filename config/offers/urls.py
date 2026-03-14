from django.urls import path
from . import views

app_name = 'offers'

urlpatterns = [
    path('', views.offers_list, name='list'),
    path('<int:offer_id>/', views.offer_detail, name='detail'),
    path('apply-to-cart/', views.apply_offer_to_cart, name='apply_to_cart'),
]