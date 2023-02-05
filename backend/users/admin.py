from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import ShoppingCart, Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'username',
                    'first_name',
                    'last_name',
                    'email',
                    )
    search_fields = ('username',
                     'first_name',
                     'last_name',
                     'email',
                     )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'follower',
                    'following',
                    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'user',
                    'recipe',
                    )


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
