from django.contrib import admin
from .models import User

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id","full_name", "phone_number","email", "is_staff","is_active","created_at", "updated_at")
    search_fields = ("full_name__contains", "phone_number__contains", "email__contains")
    list_filter = ("is_staff","is_active","created_at", "updated_at")
