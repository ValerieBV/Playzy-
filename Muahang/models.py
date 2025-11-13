# muahang/models.py
from django.db import models
from django.contrib.auth.models import User
from Sanpham.models import SanPham


# GIỎ HÀNG (dành cho cả khách & người đăng nhập)
class GioHang(models.Model):
    # Cho phép null để lưu giỏ cho khách
    nguoi_dung = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ngay_cap_nhat = models.DateTimeField(auto_now_add=True)

    # Tổng tiền giỏ hàng
    def tong_tien(self):
        return sum(item.thanh_tien() for item in self.items.all())

    # Tổng số lượng sản phẩm trong giỏ hàng
    def tong_so_luong(self):  # Cẩm đã sửa - thêm method này
        return sum(item.so_luong for item in self.items.all())

    def __str__(self):
        if self.nguoi_dung:
            return f"Giỏ hàng của {self.nguoi_dung.username}"
        return f"Giỏ hàng khách #{self.id}"

    class Meta:
        verbose_name = "Giỏ hàng"
        verbose_name_plural = "Giỏ hàng"


# sản phẩm trong giỏ hàng
class GioHangItem(models.Model):
    gio_hang = models.ForeignKey(GioHang, on_delete=models.CASCADE, related_name='items')
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE, to_field='ma_sp') #cẩm thêm to_field
    so_luong = models.PositiveIntegerField(default=1)

    def thanh_tien(self):
        # (Sửa lại logic này để dùng giá đã giảm) - cẩm them cho bài cẩm
        return self.san_pham.gia_da_giam * self.so_luong

    class Meta:
        verbose_name = "Sản phẩm trong giỏ hàng"
        verbose_name_plural = "Sản phẩm trong giỏ hàng"

# Đơn hàng
class DonHang(models.Model):
    TRANG_THAI_CHOICES = [
        ('cho_xac_nhan','Chờ xác nhận'),
        ('dang_giao', 'Đang giao'),
        ('da_giao', 'Đã giao'),
        ('that_bai', 'Thất bại'),
    ]
    PAYMENT_CHOICES = [
        ('COD', 'Thanh toán khi nhận hàng (COD)'),
        ('VNPAY', 'Thẻ ATM (App bank)/ Thẻ tín dụng (Credit Card)/ Thẻ ghi nợ (Debit Card))'),
        ('ZALOPAY', 'Ví điện tử ZaloPay'),
        ('MOMO', 'Ví MoMo'),
    ]

    nguoi_dung = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='COD', verbose_name="Phương thức thanh toán")
    ho_ten = models.CharField(max_length=100)
    so_dien_thoai = models.CharField(max_length=20)
    email = models.EmailField()
    dia_chi = models.TextField()
    tinh = models.CharField(max_length=50)
    phuong_xa = models.CharField(max_length=50)
    ghi_chu = models.TextField(blank=True, default='')
    ngay_dat = models.DateTimeField(auto_now_add=True)

    tong_tien = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phi_van_chuyen = models.IntegerField(default=30000)  # phí vận chuyển cố định
    so_tien_duoc_giam = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ma_voucher = models.CharField(max_length=50, blank=True, null=True)  # Voucher áp dụng tự động nếu có
    trang_thai = models.CharField(max_length=50, choices=TRANG_THAI_CHOICES, default='cho_xac_nhan')

    def __str__(self):
        return f"Đơn #{self.id} - {self.ho_ten}"

    # Tổng thanh toán thực tế
    def tong_thanh_toan(self):
        return self.tong_tien + self.phi_van_chuyen - self.so_tien_duoc_giam

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Lịch sử mua hàng"


#Đơn hàng Item
class DonHangItem(models.Model):
    don_hang = models.ForeignKey(DonHang, on_delete=models.CASCADE, related_name='items')
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE, to_field='ma_sp') #cẩm thêm to_field
    so_luong = models.PositiveIntegerField()
    gia = models.DecimalField(max_digits=10, decimal_places=2)

    def thanh_tien(self):
        return self.so_luong * self.gia

    class Meta:
        verbose_name = "Sản phẩm trong đơn hàng"
        verbose_name_plural = "Sản phẩm trong đơn hàng"


# trạng thái đơn hàng

class TrangThaiDonHang(models.Model):
    STATUS_CHOICES = [
        ('Cho xac nhan','Chờ xác nhận'),
        ('Dang giao', 'Đang giao'),
        ('Thanh cong', 'Thành công'),
        ('That bai', 'Thất bại'),
    ]

    don_hang = models.ForeignKey(DonHang, on_delete=models.CASCADE, related_name='lich_su_trang_thai')
    noi_dung = models.CharField(max_length=50, choices=STATUS_CHOICES)
    thoi_gian = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.don_hang} - {self.noi_dung}"

    class Meta:
        verbose_name = "Trạng thái đơn hàng"
        verbose_name_plural = "Theo dõi đơn hàng"

