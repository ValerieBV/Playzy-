from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from .models import KhoHang, LichSuGiaoDich
from Sanpham.models import SanPham
from .views import lich_su_giao_dich_view, chi_tiet_kho_hang_view
from django.shortcuts import render

@admin.register(KhoHang)
class KhoHangAdmin(admin.ModelAdmin):
    list_display = ('ma_sp', 'ten_san_pham', 'danh_muc', 'don_vi_tinh', 'so_luong_ton_kho', 'don_gia_mua')
    list_display_links = ('ma_sp', 'ten_san_pham')
    search_fields = ('ma_sp__ma_sp', 'ma_sp__ten_sp', 'ma_sp__danh_muc__ten_danh_muc')
    list_filter = ('ma_sp__danh_muc__ten_danh_muc',)#cẩm sửa dòng này
    ordering = ('ma_sp',)
    list_per_page = 20

    class Meta:
        verbose_name = "Chi tiết kho hàng"
        verbose_name_plural = "Chi tiết kho hàng"

    # Thêm phần override URL
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "",  # trang gốc của model trong admin
                self.admin_site.admin_view(self.show_custom_template),
                name="chitietkhohang_changelist",
            ),
        ]
        return custom_urls + urls

    def show_custom_template(self, request):
        """Render template tuỳ chỉnh giống Lịch sử giao dịch"""
        return chi_tiet_kho_hang_view(request)

    def ten_san_pham(self, obj):
        return obj.ma_sp.ten_sp
    ten_san_pham.short_description = "Tên sản phẩm"

    def danh_muc(self, obj):
        return obj.ma_sp.danh_muc.ten_danh_muc
    danh_muc.short_description = "Danh mục"

    def don_vi_tinh(self, obj):
        return obj.ma_sp.don_vi_tinh
    don_vi_tinh.short_description = "Đơn vị tính"

    def don_gia_mua(self, obj):
        return obj.ma_sp.don_gia_mua
    don_gia_mua.short_description = "Đơn giá mua"


@admin.register(LichSuGiaoDich)
class LichSuGiaoDichAdmin(admin.ModelAdmin):
    """
    Hiển thị giao diện 'lich_su_giao_dich.html' ngay trong Django admin
    mà không tạo thêm file wrapper.
    """
    list_display = ('ma_giao_dich', 'ma_sp', 'loai_giao_dich', 'so_luong_thay_doi', 'thoi_gian_thuc_hien')
    search_fields = ('ma_giao_dich', 'ma_sp__ten_sp')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "",  # đường dẫn gốc của model trong admin
                self.admin_site.admin_view(self.show_custom_template),
                name="lichsugiaodich_changelist",
            ),
        ]
        return custom_urls + urls

    def show_custom_template(self, request):
        """
        Render thẳng template 'kho_hang/lich_su_giao_dich.html'
        (đã có sẵn trong thư mục templates của bạn)
        """
        return lich_su_giao_dich_view(request)
from django.contrib.admin.sites import site

def them_giao_dich_view(request):
    context = {
        **site.each_context(request),  # Inject Jazzmin admin context
    }
    return render(request, "kho_hang/them_giao_dich.html", context)
