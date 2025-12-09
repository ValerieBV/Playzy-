from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import NguoiDung


# ===========================
# 1. HIỂN THỊ VAI TRÒ TRONG USERADMIN
# ===========================
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    # Cho phép tìm kiếm
    search_fields = ("username", "email")


# Gỡ UserAdmin mặc định để đăng ký lại
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ===========================
# 2. ADMIN CHO NGUOIDUNG (CỦA BẠN)
# ===========================
@admin.register(NguoiDung)
class NguoiDungAdmin(admin.ModelAdmin):
    list_display = ('user', 'ho_ten', 'sdt', 'dia_chi', 'ngay_sinh', 'vai_tro')
    search_fields = ('user__username', 'ho_ten', 'sdt')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__is_staff=False, user__is_superuser=False)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_staff=False, is_superuser=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
