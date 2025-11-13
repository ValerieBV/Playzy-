from django.db import models
from django.contrib.auth.models import User

class NguoiDung(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Tên người dùng:")
    ho_ten = models.CharField(max_length=100, verbose_name="Họ và tên:")
    sdt = models.CharField(max_length=20, verbose_name="SĐT:")
    dia_chi = models.CharField(max_length=255, verbose_name="Địa chỉ:")
    ngay_sinh = models.DateField(verbose_name="Ngày sinh:")

    def __str__(self):
        return self.ho_ten

    class Meta:
        verbose_name = "Người dùng"  # Tên khi tạo/hiển thị riêng lẻ
        verbose_name_plural = "Thông tin cá nhân"  # Tên hiển thị trên sidebar

