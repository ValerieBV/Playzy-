from django.core.management.base import BaseCommand
from Lienhe.models import CauHoiThuongGap
import sys

class Command(BaseCommand):
    help = 'Seed câu hỏi thường gặp vào database'

    def handle(self, *args, **options):
        # Cấu hình encoding để hiển thị tiếng Việt
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        
        # Danh sách câu hỏi và câu trả lời
        faqs = [
            {
                'cau_hoi': 'Shop hiện đang bán những loại board game nào?',
                'cau_tra_loi': 'Playzy hiện đang cung cấp đa dạng các loại board game phong phú, bao gồm:\n\n'
                              '• Board game chiến thuật: Cờ tỷ phú, Catan, Ticket to Ride\n'
                              '• Board game gia đình: UNO, Cờ cá ngựa, Bầu cua cá cọp\n'
                              '• Board game giáo dục: Timeline, City of Zombies\n'
                              '• Board game party: Cards Against Humanity, Exploding Kittens\n'
                              '• Board game hợp tác: Pandemic, Forbidden Island\n\n'
                              'Bạn có thể xem chi tiết tại trang Danh mục sản phẩm của chúng tôi.'
            },
            {
                'cau_hoi': 'Board game này phù hợp cho độ tuổi nào?',
                'cau_tra_loi': 'Mỗi board game đều có độ tuổi khuyến nghị được ghi rõ trên bao bì và trong mô tả sản phẩm:\n\n'
                              '• Trẻ em (6+): Các game đơn giản như UNO, Cờ cá ngựa\n'
                              '• Thanh thiếu niên (12+): Game có độ phức tạp vừa phải như Cờ tỷ phú\n'
                              '• Người lớn (16+): Game chiến thuật phức tạp như Catan, Ticket to Ride\n'
                              '• Mọi lứa tuổi: Game gia đình như Bầu cua cá cọp\n\n'
                              'Bạn có thể lọc sản phẩm theo độ tuổi trên trang Danh mục để tìm game phù hợp nhất.'
            },
            {
                'cau_hoi': 'Shop có bản mở rộng (expansion) cho game này không?',
                'cau_tra_loi': 'Có! Playzy cung cấp nhiều bản mở rộng cho các board game phổ biến:\n\n'
                              '• Catan: Các expansion như Seafarers, Cities & Knights\n'
                              '• Ticket to Ride: Europe, Asia, và nhiều bản mở rộng khác\n'
                              '• UNO: Các phiên bản đặc biệt và expansion pack\n\n'
                              'Bạn có thể tìm kiếm expansion bằng cách nhập tên game chính kèm từ khóa "expansion" hoặc "mở rộng" trong ô tìm kiếm. '
                              'Hoặc liên hệ với chúng tôi để được tư vấn cụ thể về expansion phù hợp với game bạn đang sở hữu.'
            },
            {
                'cau_hoi': 'Có thể xem hướng dẫn chơi hoặc video demo ở đâu?',
                'cau_tra_loi': 'Bạn có thể tìm hướng dẫn chơi và video demo board game tại:\n\n'
                              '• Trang chi tiết sản phẩm: Mỗi sản phẩm đều có phần mô tả và hướng dẫn cơ bản\n'
                              '• Kênh YouTube của Playzy: Chúng tôi thường xuyên đăng video hướng dẫn và review game\n'
                              '• Trang Tin tức: Các bài viết hướng dẫn chi tiết cách chơi các game phổ biến\n'
                              '• Liên hệ trực tiếp: Nhân viên tư vấn của chúng tôi sẵn sàng hướng dẫn bạn qua hotline hoặc chat\n\n'
                              'Ngoài ra, nhiều board game đi kèm sách hướng dẫn chi tiết bằng tiếng Việt trong hộp sản phẩm.'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for faq_data in faqs:
            faq, created = CauHoiThuongGap.objects.get_or_create(
                cau_hoi=faq_data['cau_hoi'],
                defaults={
                    'cau_tra_loi': faq_data['cau_tra_loi'],
                    'hien_thi': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Đã tạo câu hỏi: {faq_data["cau_hoi"]}')
                )
            else:
                # Cập nhật nếu đã tồn tại
                faq.cau_tra_loi = faq_data['cau_tra_loi']
                faq.hien_thi = True
                faq.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Đã cập nhật câu hỏi: {faq_data["cau_hoi"]}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Hoàn thành! Đã tạo {created_count} câu hỏi mới và cập nhật {updated_count} câu hỏi.'
            )
        )

