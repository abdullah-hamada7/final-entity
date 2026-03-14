from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
from products import views as product_views
from django.views.generic import TemplateView, RedirectView
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap
from products.models import Product
from offers.models import Offer

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", product_views.home, name="home"),
    path("products/", include("products.urls")),
    path("orders/", include("orders.urls")),
    path("users/", include("users.urls")),
    path("offers/", include("offers.urls")),
    path("contact/", include("contact.urls")),
    path("", RedirectView.as_view(url="/", permanent=False), name="index"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),
]


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return getattr(obj, "updated_at", None)


class OfferSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Offer.objects.all()


sitemaps = {
    "products": ProductSitemap,
    "offers": OfferSitemap,
}

urlpatterns += [
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

# إعداد عرض الملفات في وضع التطوير فقط
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# تخصيص لوحة الإدارة
admin.site.site_header = "Entity Medical Admin"
admin.site.site_title = "Entity Medical"
admin.site.index_title = "Welcome to Entity Medical Administration"
