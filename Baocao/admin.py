from django.contrib import admin
from .models import BaoCao

@admin.register(BaoCao)
class BaoCaoAdmin(admin.ModelAdmin):
    list_display = ('ma_bao_cao', 'loai_bao_cao', 'ngay_bao_cao', 'ghi_chu')
    search_fields = ('ma_bao_cao', 'loai_bao_cao')
    list_filter = ('loai_bao_cao', 'ngay_bao_cao')
