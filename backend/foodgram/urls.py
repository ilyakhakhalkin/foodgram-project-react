from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls'))

]
