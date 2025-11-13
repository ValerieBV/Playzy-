from django.db import models
from django.utils import timezone
from django.apps import apps
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()


class BaoCao(models.Model):
    ma_bao_cao = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Mã báo cáo",
    )
    loai_bao_cao = models.CharField(
        max_length=50,
        default="doanhthu",
        verbose_name="Loại báo cáo",
    )
    ngay_bao_cao = models.DateField(
        default=timezone.now,
        verbose_name="Ngày báo cáo",
    )
    ghi_chu = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ghi chú",
    )

    # Các chỉ số tổng
    tong_khach_hang = models.IntegerField(
        default=0,
        verbose_name="Tổng khách hàng",
    )
    so_don_hang = models.IntegerField(
        default=0,
        verbose_name="Số đơn hàng",
    )
    tong_doanh_thu = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Tổng doanh thu",
    )
    loi_nhuan = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Lợi nhuận",
    )

    # Dữ liệu cho Chart.js
    data_time_series = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Dữ liệu chuỗi thời gian",
    )
    data_top_products = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Sản phẩm bán chạy",
    )
    data_complaints = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Khiếu nại/hỗ trợ",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Người tạo",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật",
    )

    class Meta:
        ordering = ["-ngay_bao_cao"]
        db_table = "bao_cao"
        verbose_name = "Báo cáo"
        verbose_name_plural = "Danh sách báo cáo"

    def __str__(self):
        return f"{self.ma_bao_cao} - {self.loai_bao_cao}"

    # -------------------------
    # ✅ TÍNH DOANH THU TỰ ĐỘNG
    # -------------------------
    def compute_from_period(self, start_date, end_date):

        # Tự load models — không bị lỗi app name
        DonHang = apps.get_model("Muahang", "DonHang")
        DonHangItem = apps.get_model("Muahang", "DonHangItem")

        try:
            YeuCauHoTro = apps.get_model("Muahang", "YeuCauHoTro")
        except:
            YeuCauHoTro = None

        # Lấy đơn hàng theo khoảng thời gian
        orders = DonHang.objects.filter(
            ngay_dat__date__gte=start_date,
            ngay_dat__date__lte=end_date
        )

        self.so_don_hang = orders.count()
        self.tong_khach_hang = orders.values("nguoi_dung").distinct().count()

        # ✅ Tổng doanh thu
        from django.db.models import F, Sum, DecimalField, ExpressionWrapper

        tong_dt = orders.aggregate(
            total=Sum("tong_tien")
        )["total"] or Decimal("0")

        if tong_dt == 0:
            tong_dt = DonHangItem.objects.filter(don_hang__in=orders).aggregate(
                total=Sum(
                    ExpressionWrapper(
                        F("so_luong") * F("gia"),
                        output_field=DecimalField()
                    )
                )
            )["total"] or Decimal("0")

        self.tong_doanh_thu = tong_dt

        # ✅ Lợi nhuận mặc định = 30%
        self.loi_nhuan = self.tong_doanh_thu * Decimal("0.30")

        # ✅ TOP SẢN PHẨM
        top = DonHangItem.objects.filter(don_hang__in=orders).values(
            "san_pham__ten"
        ).annotate(
            soluong=Sum("so_luong")
        ).order_by("-soluong")[:6]

        self.data_top_products = [
            {"ten": t["san_pham__ten"], "so_luong": t["soluong"]}
            for t in top
        ]

        # ✅ Time series theo tháng
        from django.db.models.functions import TruncMonth

        series = orders.annotate(
            month=TruncMonth("ngay_dat")
        ).values("month").annotate(
            total=Sum("tong_tien")
        ).order_by("month")

        self.data_time_series = [
            {"label": s["month"].strftime("%Y-%m"), "value": float(s["total"])}
            for s in series
        ]

        # ✅ Khiếu nại / hỗ trợ
        if YeuCauHoTro:
            complaints = YeuCauHoTro.objects.filter(
                ngay_tao__date__gte=start_date,
                ngay_tao__date__lte=end_date
            ).values("loai_yeu_cau").annotate(
                c=models.Count("id")
            )

            self.data_complaints = {
                c["loai_yeu_cau"]: c["c"] for c in complaints
            }

        self.save()

        return True


