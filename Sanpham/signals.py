from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import SanPham
from Khohang.models import KhoHang


# Flag để tránh vòng lặp vô hạn
_syncing_from_khohang = False


def generate_ma_kho_hang():
    """Tạo mã kho hàng tự động và unique"""
    from Khohang.models import KhoHang
    
    # Lấy tất cả mã kho hàng hiện có
    existing_codes = set(KhoHang.objects.values_list('ma_kho_hang', flat=True))
    
    # Tìm mã kho hàng lớn nhất
    last_kho = KhoHang.objects.order_by('-ma_kho_hang').first()
    
    if last_kho:
        try:
            last_number = int(last_kho.ma_kho_hang.replace('KH', ''))
            new_number = last_number + 1
        except ValueError:
            new_number = 1
    else:
        new_number = 1
    
    # Tạo mã mới và kiểm tra unique, tăng dần cho đến khi tìm được mã chưa tồn tại
    max_attempts = 1000
    attempt = 0
    while attempt < max_attempts:
        ma_kho_hang = f'KH{new_number:04d}'
        if ma_kho_hang not in existing_codes:
            return ma_kho_hang
        new_number += 1
        attempt += 1
    
    # Nếu không tìm được trong 1000 lần thử, dùng timestamp
    import time
    return f'KH{int(time.time()) % 10000:04d}'


@receiver(pre_save, sender=SanPham)
def store_old_so_luong(sender, instance, **kwargs):
    """Lưu giá trị so_luong cũ để so sánh"""
    if instance.pk:
        try:
            old_instance = SanPham.objects.get(pk=instance.pk)
            instance._old_so_luong = old_instance.so_luong
        except SanPham.DoesNotExist:
            instance._old_so_luong = None
    else:
        instance._old_so_luong = None


@receiver(post_save, sender=SanPham)
def sync_sanpham_to_khohang(sender, instance, created, **kwargs):
    """
    Tự động đồng bộ sản phẩm với kho hàng:
    - Khi tạo sản phẩm mới: tự động tạo bản ghi kho hàng với số lượng = so_luong của sản phẩm
    - Khi cập nhật sản phẩm: đồng bộ số lượng tồn kho với số lượng sản phẩm
    """
    global _syncing_from_khohang
    
    # Tránh vòng lặp: nếu đang đồng bộ từ kho hàng thì không đồng bộ ngược lại
    if _syncing_from_khohang:
        return
    
    try:
        # Kiểm tra xem đã có kho hàng chưa
        kho_hang_exist = KhoHang.objects.filter(ma_sp=instance).first()
        
        if not kho_hang_exist:
            # Tạo kho hàng mới, model sẽ tự động tạo mã kho hàng unique trong save()
            kho_hang = KhoHang.objects.create(
                ma_sp=instance,
                so_luong_ton_kho=instance.so_luong
            )
            created_kho = True
        else:
            kho_hang = kho_hang_exist
            created_kho = False
        
        # Nếu kho hàng đã tồn tại và số lượng sản phẩm thay đổi
        if not created_kho:
            old_so_luong = getattr(instance, '_old_so_luong', None)
            # Chỉ đồng bộ nếu số lượng thực sự thay đổi
            if old_so_luong is not None and old_so_luong != instance.so_luong:
                if kho_hang.so_luong_ton_kho != instance.so_luong:
                    kho_hang.so_luong_ton_kho = instance.so_luong
                    kho_hang.save(update_fields=['so_luong_ton_kho'])
            elif created:  # Nếu là sản phẩm mới
                if kho_hang.so_luong_ton_kho != instance.so_luong:
                    kho_hang.so_luong_ton_kho = instance.so_luong
                    kho_hang.save(update_fields=['so_luong_ton_kho'])
    except Exception as e:
        print(f"Lỗi đồng bộ sản phẩm với kho hàng: {e}")


@receiver(post_delete, sender=SanPham)
def delete_khohang_when_sanpham_deleted(sender, instance, **kwargs):
    """
    Xóa bản ghi kho hàng khi xóa sản phẩm
    """
    try:
        KhoHang.objects.filter(ma_sp=instance).delete()
    except Exception as e:
        print(f"Lỗi xóa kho hàng khi xóa sản phẩm: {e}")

