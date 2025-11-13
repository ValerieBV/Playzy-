from django.db import models
from django.core.validators import MinValueValidator
from Sanpham.models import SanPham
from Muahang.models import DonHang


class KhoHang(models.Model):
    """Bảng quản lý tồn kho theo sản phẩm"""
    ma_kho_hang = models.CharField(
        max_length=6,
        primary_key=True,
        default='KH0001',
        verbose_name="Mã kho hàng"
    )

    ma_sp = models.ForeignKey(
        SanPham,
        on_delete=models.CASCADE,
        db_column='MaSP',
        related_name='kho_hang',
        verbose_name="Sản phẩm"
    )

    so_luong_ton_kho = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name="Số lượng tồn kho"
    )

    thoi_gian_cap_nhat = models.DateTimeField(
        auto_now=True,
        verbose_name="Thời gian cập nhật"
    )

    def __str__(self):
        return f"{self.ma_sp.TenSP} - Tồn: {self.so_luong_ton_kho}"

    @property
    def trang_thai_ton(self):
        """Trạng thái tồn kho: Còn hàng / Hết hàng"""
        return "Còn hàng" if self.so_luong_ton_kho > 0 else "Hết hàng"
    class Meta:
        verbose_name = "Chi tiết kho hàng"
        verbose_name_plural = "Chi tiết kho hàng"

class LichSuGiaoDich(models.Model):
    """Lịch sử nhập, xuất, điều chỉnh kho"""
    LOAI_GD_CHOICES = [
        ('NHAP', 'Nhập kho'),
        ('XUAT', 'Xuất kho'),
        ('DIEU_CHINH', 'Điều chỉnh'),
    ]

    ma_giao_dich = models.AutoField(primary_key=True)
    ma_sp = models.ForeignKey(
        SanPham,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Sản phẩm"
    )
    don_hang = models.ForeignKey(
        DonHang,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Đơn hàng liên quan"
    )
    loai_giao_dich = models.CharField(
        max_length=50,
        choices=LOAI_GD_CHOICES,
        verbose_name="Loại giao dịch"
    )
    so_luong_thay_doi = models.IntegerField(
        verbose_name="Số lượng thay đổi"
    )
    thoi_gian_thuc_hien = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Thời gian thực hiện"
    )
    ghi_chu = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ghi chú"
    )

    class Meta:
        verbose_name_plural = "Lịch sử giao dịch"
        ordering = ['-thoi_gian_thuc_hien']

    def __str__(self):
        return f"{self.loai_giao_dich} - {self.ma_sp.TenSP if self.ma_sp else 'Không rõ'} - {self.so_luong_thay_doi}"

    def save(self, *args, **kwargs):
        """Ghi lại giao dịch và tự động cập nhật tồn kho"""
        super().save(*args, **kwargs)

        if self.ma_sp:
            try:
                kho, _ = KhoHang.objects.get_or_create(ma_sp=self.ma_sp)
                # Cập nhật tồn kho sau khi ghi giao dịch
                if self.loai_giao_dich == 'NHAP':
                    kho.so_luong_ton_kho += abs(self.so_luong_thay_doi)
                elif self.loai_giao_dich == 'XUAT':
                    kho.so_luong_ton_kho = max(0, kho.so_luong_ton_kho - abs(self.so_luong_thay_doi))
                elif self.loai_giao_dich == 'DIEU_CHINH':
                    kho.so_luong_ton_kho = max(0, kho.so_luong_ton_kho + self.so_luong_thay_doi)

                kho.save()
            except Exception as e:
                print(f"Lỗi cập nhật tồn kho sau giao dịch: {e}")
    @property
    def ma_hang(self):
        return self.ma_sp

    @ma_hang.setter
    def ma_hang(self, value):
        self.ma_sp = value
