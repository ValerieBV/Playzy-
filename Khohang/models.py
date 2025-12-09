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

    def save(self, *args, **kwargs):
        """Tự động tạo mã kho hàng nếu chưa có hoặc bị trùng"""
        import time
        
        # Chỉ tạo mã kho hàng nếu chưa có hoặc đang dùng giá trị default
        if not self.ma_kho_hang or self.ma_kho_hang == 'KH0001' or not self.pk:
            # Lấy mã kho hàng lớn nhất hiện tại
            if self.pk:
                last_kho = KhoHang.objects.exclude(pk=self.pk).order_by('-ma_kho_hang').first()
            else:
                last_kho = KhoHang.objects.order_by('-ma_kho_hang').first()
            
            if last_kho:
                try:
                    last_number = int(last_kho.ma_kho_hang.replace('KH', ''))
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1
            
            # Tạo mã mới và kiểm tra unique bằng cách query database mỗi lần
            max_attempts = 1000
            attempt = 0
            while attempt < max_attempts:
                ma_kho_hang = f'KH{new_number:04d}'
                # Kiểm tra lại trong database mỗi lần để tránh race condition
                if not KhoHang.objects.filter(ma_kho_hang=ma_kho_hang).exclude(pk=self.pk if self.pk else None).exists():
                    self.ma_kho_hang = ma_kho_hang
                    break
                new_number += 1
                attempt += 1
            
            # Nếu không tìm được trong 1000 lần thử, dùng timestamp với format KHXXXX (4 số)
            if attempt >= max_attempts:
                timestamp_code = f'KH{int(time.time() * 1000) % 10000:04d}'
                # Đảm bảo timestamp code cũng unique bằng cách query database
                max_timestamp_attempts = 100
                timestamp_attempt = 0
                while KhoHang.objects.filter(ma_kho_hang=timestamp_code).exclude(pk=self.pk if self.pk else None).exists() and timestamp_attempt < max_timestamp_attempts:
                    time.sleep(0.001)  # Đợi 1ms để timestamp thay đổi
                    timestamp_code = f'KH{int(time.time() * 1000) % 10000:04d}'
                    timestamp_attempt += 1
                self.ma_kho_hang = timestamp_code
        
        # Thử save với retry nếu vẫn bị conflict
        max_retries = 3
        for retry in range(max_retries):
            try:
                super().save(*args, **kwargs)
                break
            except Exception as e:
                if 'UNIQUE constraint' in str(e) or 'unique' in str(e).lower():
                    if retry < max_retries - 1:
                        # Nếu bị conflict, tạo lại mã kho hàng với timestamp
                        timestamp_code = f'KH{int(time.time() * 1000) % 10000:04d}'
                        max_timestamp_attempts = 100
                        timestamp_attempt = 0
                        while KhoHang.objects.filter(ma_kho_hang=timestamp_code).exclude(pk=self.pk if self.pk else None).exists() and timestamp_attempt < max_timestamp_attempts:
                            time.sleep(0.001)
                            timestamp_code = f'KH{int(time.time() * 1000) % 10000:04d}'
                            timestamp_attempt += 1
                        self.ma_kho_hang = timestamp_code
                    else:
                        raise
                else:
                    raise

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
