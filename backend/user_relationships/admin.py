from django.contrib import admin
from .models import UserRelationship, IkitaiStatus

# Register your models here.

@admin.register(UserRelationship)
class UserRelationshipAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('follower__username', 'followed__username')

@admin.register(IkitaiStatus)
class IkitaiStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'expires_at', 'created_at')
    search_fields = ('user__username',)
