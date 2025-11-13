from django.db import models

class BaiViet(models.Model):
    tieu_de = models.CharField(max_length=255)
    noi_dung = models.TextField()
    anh_dai_dien = models.ImageField(upload_to='Tintuc/', blank=True, null=True)
    ngay_dang = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-ngay_dang']
        verbose_name = "Bài viết"
        verbose_name_plural = "Bài viết"

    def __str__(self):
        return self.tieu_de
