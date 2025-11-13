from django.core.management.base import BaseCommand
from datetime import date, timedelta
from Baocao.models import BaoCao


class Command(BaseCommand):
    help = "Tự động tạo báo cáo doanh thu mỗi ngày"

    def handle(self, *args, **options):

        today = date.today()
        start_date = today - timedelta(days=30)

        ma = f"AUTO_{today.strftime('%Y%m%d')}"

        bc, created = BaoCao.objects.get_or_create(
            ma_bao_cao=ma,
            defaults={"ngay_bao_cao": today}
        )

        bc.compute_from_period(start_date, today)

        self.stdout.write(self.style.SUCCESS(f"✅ Đã tạo báo cáo {ma}"))
