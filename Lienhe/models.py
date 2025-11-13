from django.db import models

class CauHoiThuongGap(models.Model):
    cau_hoi = models.CharField(
        max_length=255,
        verbose_name="Câu hỏi"
    )
    cau_tra_loi = models.TextField(
        blank=True,
        null=True,
        verbose_name="Câu trả lời"
    )
    hien_thi = models.BooleanField(
        default=True,
        verbose_name="Hiển thị"
    )
    ngay_tao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )

    class Meta:
        db_table = "cau_hoi_thuong_gap"
        verbose_name = "Câu hỏi thường gặp"
        verbose_name_plural = "Danh sách câu hỏi thường gặp"
        ordering = ['-ngay_tao']

    def __str__(self):
        return self.cau_hoi

