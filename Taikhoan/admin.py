from django.contrib import admin
from .models import NguoiDung
from django.contrib.auth.models import User

@admin.register(NguoiDung)
class NguoiDungAdmin(admin.ModelAdmin):
    list_display = ('user', 'ho_ten', 'sdt', 'dia_chi', 'ngay_sinh')
    search_fields = ('user__username', 'ho_ten', 'sdt')


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__is_staff=False, user__is_superuser=False)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Chỉ hiện user là khách hàng (không phải admin) khi chọn User"""
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_staff=False, is_superuser=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
