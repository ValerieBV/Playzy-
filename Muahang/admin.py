from django.contrib import admin
from .models import GioHang, GioHangItem, DonHang, DonHangItem, TrangThaiDonHang


class GioHangItemInline(admin.TabularInline):
    model = GioHangItem
    extra = 0
    readonly_fields = ('san_pham', 'so_luong', 'thanh_tien_display')
    can_delete = False
    
    def thanh_tien_display(self, obj):
        return f"{obj.thanh_tien():,.0f}₫"
    thanh_tien_display.short_description = "Thành tiền"
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(GioHang)
class GioHangAdmin(admin.ModelAdmin):
    list_display = ('id', 'nguoi_dung', 'tong_tien_display', 'tong_so_luong_display', 'ngay_cap_nhat')
    list_filter = ('ngay_cap_nhat',)
    search_fields = ('nguoi_dung__username', 'nguoi_dung__email')
    readonly_fields = ('ngay_cap_nhat', 'tong_tien_display', 'tong_so_luong_display')
    inlines = [GioHangItemInline]
    
    def tong_tien_display(self, obj):
        return f"{obj.tong_tien():,.0f}₫"
    tong_tien_display.short_description = "Tổng tiền"
    
    def tong_so_luong_display(self, obj):
        return obj.tong_so_luong()
    tong_so_luong_display.short_description = "Tổng số lượng"
    
    fieldsets = (
        ('Thông tin giỏ hàng', {
            'fields': ('nguoi_dung', 'ngay_cap_nhat', 'tong_tien_display', 'tong_so_luong_display')
        }),
    )


class DonHangItemInline(admin.TabularInline):
    model = DonHangItem
    extra = 0
    readonly_fields = ('san_pham', 'so_luong', 'gia', 'thanh_tien_display')
    can_delete = False
    
    def thanh_tien_display(self, obj):
        return f"{obj.thanh_tien():,.0f}₫"
    thanh_tien_display.short_description = "Thành tiền"
    
    def has_add_permission(self, request, obj=None):
        return False


class TrangThaiDonHangInline(admin.TabularInline):
    model = TrangThaiDonHang
    extra = 0
    readonly_fields = ('noi_dung', 'thoi_gian')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(DonHang)
class DonHangAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ho_ten',
        'nguoi_dung',
        'tong_tien_display',
        'phi_van_chuyen_display',
        'so_tien_duoc_giam_display',
        'tong_thanh_toan_display',
        'payment_method',
        'trang_thai',
        'ngay_dat'
    )
    list_filter = ('trang_thai', 'payment_method', 'ngay_dat', 'tinh')
    search_fields = ('id', 'ho_ten', 'so_dien_thoai', 'email', 'nguoi_dung__username')
    readonly_fields = (
        'ngay_dat',
        'tong_tien',
        'phi_van_chuyen',
        'so_tien_duoc_giam',
        'tong_thanh_toan_display'
    )
    inlines = [DonHangItemInline, TrangThaiDonHangInline]
    
    fieldsets = (
        ('Thông tin khách hàng', {
            'fields': ('nguoi_dung', 'ho_ten', 'so_dien_thoai', 'email')
        }),
        ('Địa chỉ giao hàng', {
            'fields': ('dia_chi', 'phuong_xa', 'tinh')
        }),
        ('Thông tin đơn hàng', {
            'fields': (
                'ngay_dat',
                'payment_method',
                'trang_thai',
                'tong_tien',
                'phi_van_chuyen',
                'so_tien_duoc_giam',
                'ma_voucher',
                'tong_thanh_toan_display'
            )
        }),
        ('Ghi chú', {
            'fields': ('ghi_chu',)
        }),
    )
    
    def tong_tien_display(self, obj):
        return f"{obj.tong_tien:,.0f}₫"
    tong_tien_display.short_description = "Tổng tiền"
    
    def phi_van_chuyen_display(self, obj):
        return f"{obj.phi_van_chuyen:,}₫"
    phi_van_chuyen_display.short_description = "Phí vận chuyển"
    
    def so_tien_duoc_giam_display(self, obj):
        return f"{obj.so_tien_duoc_giam:,.0f}₫"
    so_tien_duoc_giam_display.short_description = "Giảm giá"
    
    def tong_thanh_toan_display(self, obj):
        return f"{obj.tong_thanh_toan():,.0f}₫"
    tong_thanh_toan_display.short_description = "Tổng thanh toán"

    actions = [
        'mark_cho_xac_nhan',
        'mark_da_xac_nhan',
        'mark_dang_giao',
        'mark_da_giao',
        'mark_thanh_cong',
        'mark_that_bai'
    ]

    def mark_cho_xac_nhan(self, request, queryset):
        queryset.update(trang_thai='cho_xac_nhan')
        for don_hang in queryset:
            TrangThaiDonHang.objects.create(
                don_hang=don_hang,
                noi_dung='Cho xac nhan'
            )
        self.message_user(request, f'Đã cập nhật {queryset.count()} đơn hàng sang trạng thái "Chờ xác nhận".')
    mark_cho_xac_nhan.short_description = "Chuyển sang 'Chờ xác nhận'"
    
    def mark_dang_giao(self, request, queryset):
        queryset.update(trang_thai='dang_giao')
        for don_hang in queryset:
            TrangThaiDonHang.objects.create(
                don_hang=don_hang,
                noi_dung='Dang giao'
            )
        self.message_user(request, f'Đã cập nhật {queryset.count()} đơn hàng sang trạng thái "Đang giao".')
    mark_dang_giao.short_description = "Chuyển sang 'Đang giao'"

    def mark_da_xac_nhan(self, request, queryset):
        queryset.update(trang_thai='da_xac_nhan')
        for don_hang in queryset:
            TrangThaiDonHang.objects.create(
                don_hang=don_hang,
                noi_dung='da_xac_nhan'
            )
        self.message_user(request, f'Đã cập nhật {queryset.count()} đơn sang "Đã xác nhận".')

    mark_da_xac_nhan.short_description = "Chuyển sang 'Đã xác nhận'"

    def mark_da_giao(self, request, queryset):
        queryset.update(trang_thai='da_giao')
        for don_hang in queryset:
            TrangThaiDonHang.objects.create(
                don_hang=don_hang,
                noi_dung='Thanh cong'
            )
        self.message_user(request, f'Đã cập nhật {queryset.count()} đơn hàng sang trạng thái "Đã giao".')
    mark_da_giao.short_description = "Chuyển sang 'Đã giao'"

    def mark_thanh_cong(self, request, queryset):
        queryset.update(trang_thai='thanh_cong')
        for don_hang in queryset:
            TrangThaiDonHang.objects.create(
                don_hang=don_hang,
                noi_dung='thanh_cong'
            )
        self.message_user(request, f'Đã cập nhật {queryset.count()} đơn sang \"Thành công\".')

    mark_thanh_cong.short_description = "Chuyển sang 'Thành công'"

    def mark_that_bai(self, request, queryset):
        queryset.update(trang_thai='that_bai')
        for don_hang in queryset:
            TrangThaiDonHang.objects.create(
                don_hang=don_hang,
                noi_dung='That bai'
            )
        self.message_user(request, f'Đã cập nhật {queryset.count()} đơn hàng sang trạng thái "Thất bại".')
    mark_that_bai.short_description = "Chuyển sang 'Thất bại'"


@admin.register(TrangThaiDonHang)
class TrangThaiDonHangAdmin(admin.ModelAdmin):
    list_display = ('id', 'don_hang', 'noi_dung', 'thoi_gian')
    list_filter = ('noi_dung', 'thoi_gian')
    search_fields = ('don_hang__id', 'don_hang__ho_ten')
    readonly_fields = ('don_hang', 'noi_dung', 'thoi_gian')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

