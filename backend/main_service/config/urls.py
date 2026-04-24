from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/excursions/', include('excursions.urls')),
    path('api/accounts/', include('accounts.urls')),

    path('accounts/', include('allauth.urls')),
    path('accounts/', include('allauth.socialaccount.urls')),

    path('api/bookings/', include('bookings.urls')),

    path('api/reviews/', include('reviews.urls')),
    path('api/wishlist/', include('wishlist.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
