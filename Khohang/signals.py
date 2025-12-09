from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import KhoHang


@receiver(pre_save, sender=KhoHang)
def store_old_so_luong_kho(sender, instance, **kwargs):
    """Lưu giá trị so_luong_ton_kho cũ để so sánh"""
    if instance.pk:
        try:
            old_instance = KhoHang.objects.get(pk=instance.pk)
            instance._old_so_luong_ton_kho = old_instance.so_luong_ton_kho
        except KhoHang.DoesNotExist:
            instance._old_so_luong_ton_kho = None
    else:
        instance._old_so_luong_ton_kho = None


@receiver(post_save, sender=KhoHang)
def sync_khohang_to_sanpham(sender, instance, created, **kwargs):
    """
    Đồng bộ ngược từ kho hàng về sản phẩm:
    - Khi cập nhật số lượng tồn kho, tự động cập nhật số lượng sản phẩm
    - Cập nhật trạng thái sản phẩm (Còn hàng / Hết hàng)
    """
    try:
        # Import ở đây để tránh circular import
        import Sanpham.signals
        
        # Đặt flag để tránh vòng lặp
        Sanpham.signals._syncing_from_khohang = True
        
        san_pham = instance.ma_sp
        old_so_luong = getattr(instance, '_old_so_luong_ton_kho', None)
        
        # Chỉ đồng bộ nếu số lượng thực sự thay đổi
        if old_so_luong is not None and old_so_luong != instance.so_luong_ton_kho:
            if san_pham.so_luong != instance.so_luong_ton_kho:
                san_pham.so_luong = instance.so_luong_ton_kho
                # Cập nhật trạng thái dựa trên số lượng tồn kho
                san_pham.trang_thai = 'CON_HANG' if instance.so_luong_ton_kho > 0 else 'HET_HANG'
                san_pham.save(update_fields=['so_luong', 'trang_thai'])
        elif created:  # Nếu là kho hàng mới
            if san_pham.so_luong != instance.so_luong_ton_kho:
                san_pham.so_luong = instance.so_luong_ton_kho
                san_pham.trang_thai = 'CON_HANG' if instance.so_luong_ton_kho > 0 else 'HET_HANG'
                san_pham.save(update_fields=['so_luong', 'trang_thai'])
    except Exception as e:
        print(f"Lỗi đồng bộ kho hàng với sản phẩm: {e}")
    finally:
        # Reset flag
        try:
            import Sanpham.signals
            Sanpham.signals._syncing_from_khohang = False
        except:
            pass

