from django.contrib import admin
from .models import BaiViet

@admin.register(BaiViet)
class BaiVietAdmin(admin.ModelAdmin):
    list_display = ('tieu_de', 'ngay_dang')
    search_fields = ('tieu_de', 'noi_dung')
