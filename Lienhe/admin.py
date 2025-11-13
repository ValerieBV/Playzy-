from django.contrib import admin
from .models import CauHoiThuongGap

@admin.register(CauHoiThuongGap)
class CauHoiThuongGapAdmin(admin.ModelAdmin):
    list_display = ('cau_hoi', 'hien_thi', 'ngay_tao')
    list_filter = ('hien_thi',)
    search_fields = ('cau_hoi',)


