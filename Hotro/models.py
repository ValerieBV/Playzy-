from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class HoSoNguoiDung(models.Model):
    VAI_TRO_LUA_CHON = (
        ('khach_hang', 'Khách hàng'),
        ('nguoi_ban', 'Người bán'),
        ('quan_tri', 'Quản trị'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='ho_so',
        verbose_name="Tài khoản"
    )
    vai_tro = models.CharField(
        max_length=20,
        choices=VAI_TRO_LUA_CHON,
        default='khach_hang',
        verbose_name="Vai trò"
    )

    def __str__(self):
        return f"{self.user.username} ({self.vai_tro})"

    class Meta:
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Hồ sơ người dùng"


class YeuCauHoTro(models.Model):
    TRANG_THAI_LUA_CHON = (
        ('cho_xu_ly', 'Chưa xử lý'),
        ('dang_xu_ly', 'Đang xử lý'),
        ('da_xu_ly', 'Đã xử lý'),
        ('dong', 'Đóng'),
    )

    LOAI_YEU_CAU = (
        ('tu_van', 'Tư vấn'),
        ('khieu_nai', 'Khiếu nại'),
        ('ho_tro', 'Hỗ trợ'),
    )

    ma_yeu_cau = models.CharField(max_length=20, unique=True, blank=True, verbose_name="Mã yêu cầu")
    khach_hang = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='yeu_cau_ho_tro',
        verbose_name="Khách hàng"
    )
    nguoi_ban = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='yeu_cau_duoc_giao',
        verbose_name="Người xử lý"
    )

    ten_san_pham = models.CharField(max_length=255, blank=True, verbose_name="Tên sản phẩm")
    loai_yeu_cau = models.CharField(max_length=30, choices=LOAI_YEU_CAU, default='tu_van', verbose_name="Loại yêu cầu")
    tieu_de = models.CharField(max_length=255, verbose_name="Tiêu đề")
    noi_dung = models.TextField(blank=True, verbose_name="Nội dung")

    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_LUA_CHON, default='cho_xu_ly', verbose_name="Trạng thái")

    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    cap_nhat_luc = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lúc")

    muc_do_uu_tien = models.IntegerField(default=3, verbose_name="Mức độ ưu tiên")  # 1–cao → 5–thấp

    class Meta:
        ordering = ['-ngay_tao']
        verbose_name = "Yêu cầu hỗ trợ"
        verbose_name_plural = "Danh sách yêu cầu hỗ trợ"

    def save(self, *args, **kwargs):
        # Auto-generate code
        if not self.ma_yeu_cau:
            prefix = 'YCV'
            super().save(*args, **kwargs)
            if not self.ma_yeu_cau:
                self.ma_yeu_cau = f"{prefix}{self.id:04d}"
                super().save(update_fields=['ma_yeu_cau'])
            return
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ma_yeu_cau} - {self.tieu_de}"


class TinNhanHoTro(models.Model):
    yeu_cau = models.ForeignKey(YeuCauHoTro, on_delete=models.CASCADE, related_name='tin_nhan', verbose_name="Yêu cầu")
    nguoi_gui = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Người gửi")
    noi_dung = models.TextField(verbose_name="Nội dung")
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    noi_bo = models.BooleanField(default=False, verbose_name="Ghi chú nội bộ")  # tin nội bộ

    class Meta:
        ordering = ['ngay_tao']
        verbose_name = "Tin nhắn hỗ trợ"
        verbose_name_plural = "Tin nhắn hỗ trợ"

    def __str__(self):
        return f"Tin nhắn #{self.id} - {self.yeu_cau.ma_yeu_cau}"


