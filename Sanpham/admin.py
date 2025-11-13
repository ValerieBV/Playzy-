from django.contrib import admin
from .models import DanhMuc, SanPham, HinhAnhSanPham, DanhGiaSanPham


@admin.register(DanhMuc)
class DanhMucAdmin(admin.ModelAdmin):
    list_display = ('ma_danh_muc', 'ten_danh_muc', 'duong_dan')
    search_fields = ('ma_danh_muc', 'ten_danh_muc')
    # Giữ nguyên: Tự động tạo slug (duong_dan)
    prepopulated_fields = {'duong_dan': ('ten_danh_muc',)}


class HinhAnhSanPhamInline(admin.TabularInline):
    model = HinhAnhSanPham
    extra = 1
    verbose_name = "Ảnh phụ"
    verbose_name_plural = "Các ảnh phụ"


class DanhGiaSanPhamInline(admin.TabularInline):
    model = DanhGiaSanPham
    extra = 0
    readonly_fields = ('ma_nguoi_dung', 'diem_danh_gia', 'binh_luan', 'ngay_danh_gia')
    can_delete = False
    verbose_name = "Đánh giá"
    verbose_name_plural = "Các đánh giá"


@admin.register(SanPham)
class SanPhamAdmin(admin.ModelAdmin):
    # === CÁC TÙY CHỈNH CHÍNH ===

    list_display = (
        'ma_sp',
        'ten_sp',
        'danh_muc',
        'gia_goc',
        'ty_le_giam_gia',
        'so_luong',
        'trang_thai',
        'hien_thi_gia_da_giam'  # Cột tính toán
    )

    # CẬP NHẬT: Thêm tất cả các bộ lọc boolean
    list_filter = (
        'danh_muc',
        'trang_thai',
        'choi_2_nguoi',
        'choi_4_nguoi',
        'choi_tren_4_nguoi',
        'tuoi_tren_6',
        'tuoi_tren_16',
        'tuoi_tren_18'
    )

    # CẬP NHẬT: Đã xóa 'tags__name'
    search_fields = ('ma_sp', 'ten_sp')

    autocomplete_fields = ['danh_muc', 'san_pham_lien_quan']

    # CẬP NHẬT: Thêm 'gia_da_giam' vào readonly
    # Bắt buộc phải có để hiển thị trong fieldsets
    readonly_fields = ('gia_da_giam',)

    # === HÀM TÍNH TOÁN CHO CỘT (Đã giải thích) ===
    def hien_thi_gia_da_giam(self, obj):
        return obj.gia_da_giam

    hien_thi_gia_da_giam.short_description = "Giá thực tế (đã giảm)"

    # === BỐ CỤC TRANG THÊM/SỬA ===
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('ma_sp', 'ten_sp', 'danh_muc', 'mo_ta')
        }),
        ('Thông tin bán hàng', {
            'fields': (
                # CẬP NHẬT: Thêm 'gia_da_giam' (readonly) vào hàng này
                ('gia_goc', 'ty_le_giam_gia', 'gia_da_giam'),
                ('so_luong', 'don_vi_tinh'),
                'trang_thai'
            )
        }),
        ('Phân loại & Thuộc tính', {
            'fields': (
                ('choi_2_nguoi', 'choi_4_nguoi', 'choi_tren_4_nguoi'),
                ('tuoi_tren_6', 'tuoi_tren_16', 'tuoi_tren_18')
            )
        }),
        ('Hình ảnh & Liên kết', {
            'fields': ('anh_dai_dien', 'san_pham_lien_quan')
        }),
    )

    # === CÁC MỤC LIÊN QUAN (Hiển thị ở dưới cùng) ===
    inlines = [HinhAnhSanPhamInline, DanhGiaSanPhamInline]