from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from pathlib import Path

from Tintuc.models import BaiViet


NEWS_ITEMS = [
    {
        "image": "image 107.png",
        "title": "5 mẹo biến buổi chơi board game tại nhà thành trải nghiệm đáng nhớ",
        "body": (
            "Không gian, âm nhạc và cách sắp xếp thành viên đều ảnh hưởng lớn đến cảm xúc của buổi chơi board game. "
            "Chỉ cần chuẩn bị một góc bàn gọn gàng, vài món ăn nhẹ và phân bổ thể lệ rõ ràng, bạn sẽ tạo ra một buổi tối đầy tiếng cười. "
            "Đừng quên ghi lại những khoảnh khắc chiến thắng bất ngờ để cả nhóm có thêm câu chuyện kể lại sau này."
        ),
    },
    {
        "image": "image 108.png",
        "title": "Cờ tỷ phú – trò chơi kinh điển vẫn hút khách trong mùa cuối năm",
        "body": (
            "Trong nhiều khảo sát về board game bán chạy cuối năm, Cờ tỷ phú luôn nằm trong top đầu nhờ luật chơi dễ nhớ và tính cạnh tranh cao. "
            "Các phiên bản mới liên tục bổ sung bản đồ thành phố, thẻ cơ hội thú vị giúp trò chơi cập nhật hơi thở hiện đại. "
            "Đây là lựa chọn hoàn hảo cho những buổi tụ họp đông người cần một trò chơi kéo dài, kịch tính."
        ),
    },
    {
        "image": "image 112.png",
        "title": "UNO – bí quyết để luôn dẫn đầu trong mọi ván bài",
        "body": (
            "UNO tưởng như chỉ phụ thuộc vào vận may nhưng người chơi lão luyện luôn có chiến thuật riêng. "
            "Quan sát màu sắc, ghi nhớ số lượng thẻ đặc biệt và điều chỉnh nhịp đánh giúp bạn kiểm soát nhịp ván bài. "
            "Nếu muốn thêm gia vị, hãy thử các biến thể UNO Flip hoặc UNO All Wild đang rất được cộng đồng yêu thích."
        ),
    },
    {
        "image": "image 129.png",
        "title": "4 lý do board game giúp kết nối gia đình hiệu quả hơn",
        "body": (
            "Một nghiên cứu từ đại học Michigan cho thấy các gia đình có thói quen chơi board game cùng nhau mỗi tuần ít mâu thuẫn hơn 30%. "
            "Các trò chơi chiến thuật nhẹ đem lại cơ hội cho trẻ em luyện tư duy logic, trong khi cha mẹ có thêm thời gian lắng nghe con. "
            "Bạn có thể bắt đầu bằng những tựa game nhẹ nhàng như Dixit, Azul hoặc Ticket to Ride phiên bản rút gọn."
        ),
    },
    {
        "image": "image 130.png",
        "title": "Xu hướng board game giáo dục quay trở lại mạnh mẽ",
        "body": (
            "Không chỉ dừng ở giải trí, các nhà xuất bản đang tung ra hàng loạt board game giúp trẻ học toán, lịch sử và kỹ năng giải quyết vấn đề. "
            "Những sản phẩm như City of Zombies hay Timeline được giáo viên tại Việt Nam đưa vào lớp học ngoại khóa để tăng tương tác. "
            "Nếu bạn muốn kết hợp vui chơi và học tập, đây là thời điểm tuyệt vời để bổ sung vào bộ sưu tập board game của gia đình."
        ),
    },
]


class Command(BaseCommand):
    help = "Seed bảng Tintuc_baiviet từ thư mục ảnh và dữ liệu mô tả."

    def add_arguments(self, parser):
        parser.add_argument(
            "--images-dir",
            type=str,
            default="image/Tin_tuc",
            help="Thư mục chứa ảnh nguồn (mặc định: image/Tin_tuc).",
        )

    def handle(self, *args, **options):
        images_dir = Path(options["images_dir"]).resolve()

        if not images_dir.exists():
            raise CommandError(f"Không tìm thấy thư mục ảnh: {images_dir}")

        created = 0
        updated = 0

        for item in NEWS_ITEMS:
            image_path = images_dir / item["image"]
            if not image_path.exists():
                self.stdout.write(self.style.WARNING(f"Bỏ qua {item['title']} - thiếu ảnh {image_path.name}"))
                continue

            obj, is_created = BaiViet.objects.get_or_create(
                tieu_de=item["title"],
                defaults={
                    "noi_dung": item["body"],
                },
            )

            if not is_created:
                obj.noi_dung = item["body"]
                updated += 1
            else:
                created += 1

            with image_path.open("rb") as f:
                obj.anh_dai_dien.save(image_path.name, ContentFile(f.read()), save=False)

            obj.save()
            self.stdout.write(self.style.SUCCESS(f"Seeded: {obj.tieu_de}"))

        self.stdout.write(self.style.SUCCESS(f"Hoàn tất. Tạo mới {created}, cập nhật {updated} bài viết."))

