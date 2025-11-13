from django.contrib import admin
from .models import HoSoNguoiDung, YeuCauHoTro, TinNhanHoTro


@admin.register(HoSoNguoiDung)
class HoSoNguoiDungAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vai_tro')
    list_filter = ('vai_tro',)
    search_fields = ('user__username', 'user__email')
    ordering = ('id',)



class TinNhanHoTroInline(admin.TabularInline):
    model = TinNhanHoTro
    fields = ('noi_dung', 'noi_bo', 'nguoi_gui', 'ngay_tao')
    readonly_fields = ('nguoi_gui', 'ngay_tao')
    extra = 0
    can_delete = False
    verbose_name = "Trao đổi"
    verbose_name_plural = "Lịch sử trao đổi"


@admin.register(YeuCauHoTro)
class YeuCauHoTroAdmin(admin.ModelAdmin):
    inlines = [TinNhanHoTroInline]

    list_display = (
        'ma_yeu_cau',
        'tieu_de',
        'khach_hang',
        'nguoi_ban',
        'trang_thai',
        'muc_do_uu_tien',
        'ngay_tao',
    )
    list_filter = ('trang_thai', 'loai_yeu_cau', 'muc_do_uu_tien')
    search_fields = ('ma_yeu_cau', 'tieu_de', 'khach_hang__username', 'nguoi_ban__username')
    readonly_fields = ('ma_yeu_cau', 'ngay_tao', 'cap_nhat_luc')
    ordering = ('-ngay_tao',)
    date_hierarchy = 'ngay_tao'

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, TinNhanHoTro) and not obj.pk:
                obj.nguoi_gui = request.user
            obj.save()
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()


@admin.register(TinNhanHoTro)
class TinNhanHoTroAdmin(admin.ModelAdmin):
    list_display = ('id', 'yeu_cau', 'nguoi_gui', 'noi_dung_rut_gon', 'noi_bo', 'ngay_tao')
    list_filter = ('noi_bo', 'ngay_tao')
    search_fields = ('yeu_cau__ma_yeu_cau', 'nguoi_gui__username', 'noi_dung')
    readonly_fields = ('ngay_tao',)

    def noi_dung_rut_gon(self, obj):
        return obj.noi_dung[:50] + ('...' if len(obj.noi_dung) > 50 else '')
    noi_dung_rut_gon.short_description = "Nội dung"



