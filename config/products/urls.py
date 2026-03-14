from django.urls import path, re_path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.products_list, name='home'),
    re_path(r'^category/(?P<slug>[-\w\u0600-\u06FF]+)/$', views.category_products, name='category'),
    re_path(r'^(?P<slug>[-\w\u0600-\u06FF]+)/$', views.product_detail, name='detail'),
    path('review/<int:product_id>/add/', views.add_review, name='add_review'),
]