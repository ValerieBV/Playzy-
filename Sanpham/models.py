# Sanpham/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify



# Bảng 1: Danh mục sản phẩm
class DanhMuc(models.Model):
    ma_danh_muc = models.CharField(max_length=6, primary_key=True, verbose_name="Mã danh mục")
    ten_danh_muc = models.CharField(max_length=255, verbose_name="Tên danh mục")
    mo_ta = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    duong_dan = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Đường dẫn")

    def save(self, *args, **kwargs):
        if not self.duong_dan:
            self.duong_dan = slugify(self.ten_danh_muc)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ten_danh_muc

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"


# Bảng 2: Sản phẩm
class SanPham(models.Model):
    TRANG_THAI_CHOICES = [
        ('CON_HANG', 'Còn hàng'),
        ('HET_HANG', 'Hết hàng'),
    ]

    ma_sp = models.CharField(max_length=6, primary_key=True, verbose_name="Mã sản phẩm")
    danh_muc = models.ForeignKey(
        DanhMuc,
        verbose_name="Danh mục",
        on_delete=models.SET_NULL,  # Hoặc models.PROTECT, ...
        null=True,  # <-- Thêm dòng này
        blank=True  # <-- Thêm dòng này
    )
    GIAM_GIA_CHOICES = [
        (0, '0%'),
        (10, '10%'),
        (20, '20%'),
        (25, '25%'),
        (30, '30%'),
        (35, '35%'),
        (40, '40%'),
        (45, '45%'),
        (50, '50%'),
        (55, '55%'),
        (60, '60%'),
        (65, '65%'),
        (70, '75%'),
        (80, '80%'),
        (85, '85%'),
        (90, '90%'),
        (95, '95%'),
        (100, '100%'),
    ]

    # Trường giá gốc
    gia_goc = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="Giá gốc"
    )

    # Trường tỷ lệ giảm giá mới
    ty_le_giam_gia = models.IntegerField(
        choices=GIAM_GIA_CHOICES,
        default=0,  # Mặc định là không giảm
        verbose_name="Mã giảm giá (%)")
    ten_sp = models.CharField(max_length=500, verbose_name="Tên sản phẩm")
    mo_ta = models.TextField(verbose_name="Mô tả",null=True, blank=True)
    so_luong = models.IntegerField(verbose_name="Số lượng")
    don_vi_tinh = models.CharField(max_length=50, blank=True, null=True, verbose_name="Đơn vị tính", default="Cái")

    # nha_cung_cap = models.CharField(
    #     max_length=255,
    #     null=True,
    #     blank=True,
    #     verbose_name="Nhà cung cấp"
    # )

    @property
    def gia_da_giam(self):
        """
        Đây là một hàm property, nó hoạt động như một
        trường (field) nhưng giá trị được tính toán động.
        """
        if self.ty_le_giam_gia == 0:
            return self.gia_goc

        giam = (self.gia_goc * self.ty_le_giam_gia) / 100
        gia_moi = self.gia_goc - giam

        # Làm tròn về số nguyên (vì bạn dùng decimal_places=0)
        return round(gia_moi)

    def __str__(self):
        return self.ten_sp

    # --- THAY ĐỔI: Chuyển 'so_nguoi_choi' sang 3 trường BooleanField ---
    # Dựa trên NGUOI_CHOI_CHOICES cũ của bạn
    choi_2_nguoi = models.BooleanField(verbose_name="2 người", default=False)
    choi_4_nguoi = models.BooleanField(verbose_name="4 người", default=False)
    choi_tren_4_nguoi = models.BooleanField(verbose_name="Trên 4 người", default=False)
    # --- KẾT THÚC THAY ĐỔI ---

    tuoi_tren_6 = models.BooleanField(verbose_name="> 6 tuổi", default=False)
    tuoi_tren_16 = models.BooleanField(verbose_name="> 16 tuổi", default=False)
    tuoi_tren_18 = models.BooleanField(verbose_name="> 18 tuổi", default=False)

    anh_dai_dien = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Ảnh đại diện")
    trang_thai = models.CharField(max_length=10, choices=TRANG_THAI_CHOICES, default='CON_HANG',
                                  verbose_name="Trạng thái")
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)
    san_pham_lien_quan = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name="Sản phẩm liên quan"
    )

    def __str__(self):
        return f"[{self.ma_sp}] {self.ten_sp}"

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"  # Bỏ số thứ tự


# Bảng 3: Hình ảnh sản phẩm
class HinhAnhSanPham(models.Model):
    ma_hinh_anh_sp = models.CharField(max_length=6, primary_key=True, verbose_name="Mã hình ảnh sản phẩm")
    ma_sp = models.ForeignKey(SanPham, on_delete=models.CASCADE, db_column='ma_sp', related_name='hinh_anh_phu', verbose_name="Mã sản phẩm")
    duong_dan = models.ImageField(upload_to='products_gallery/', verbose_name="Đường dẫn")
    ghi_chu = models.CharField(max_length=255, default="Ảnh phụ", verbose_name="Ghi chú")

    def __str__(self):
        return f"Ảnh cho {self.ma_sp.ten_sp}"

    class Meta:
        verbose_name = "Hình ảnh sản phẩm"
        verbose_name_plural = "Hình ảnh sản phẩm"


# Bảng 4: Đánh giá sản phẩm
class DanhGiaSanPham(models.Model):
    ma_danh_gia = models.CharField(max_length=6, primary_key=True,verbose_name="Mã đánh giá")
    ma_sp = models.ForeignKey(SanPham, on_delete=models.CASCADE, db_column='ma_sp', related_name='danh_gia', verbose_name="Mã sản phẩm")
    ma_nguoi_dung = models.ForeignKey(User, on_delete=models.CASCADE, db_column='ma_nguoi_dung', verbose_name="Mã người dùng")
    diem_danh_gia = models.IntegerField(verbose_name="Điểm đánh giá")
    binh_luan = models.TextField(null=True, blank=True, verbose_name="Bình luận") # Đã chuyển đổi theo ví dụ
    ngay_danh_gia = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đánh giá")

    def __str__(self):
        return f"Đánh giá cho {self.ma_sp.ten_sp} bởi {self.ma_nguoi_dung.username}"

    class Meta:
        verbose_name = "Đánh giá sản phẩm"
        verbose_name_plural = "Đánh giá sản phẩm"

