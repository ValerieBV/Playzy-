# muahang/cart.py
from .models import GioHang, GioHangItem
from Sanpham.models import SanPham
# cẩm sửa dòng trên
#Lấy giỏ hàng cho cả user & khách
def lay_gio_hang(user_or_session):
    # Nếu là user đã đăng nhập
    if hasattr(user_or_session, 'is_authenticated') and user_or_session.is_authenticated:
        gio_hang, _ = GioHang.objects.get_or_create(nguoi_dung=user_or_session)
        return gio_hang

    #  Nếu là khách: lấy giỏ từ session
    session = user_or_session
    giohang_id = session.get('giohang_id')

    if giohang_id:
        gio_hang = GioHang.objects.filter(id=giohang_id, nguoi_dung__isnull=True).first()
        if gio_hang:
            return gio_hang

    # hưa có giỏ → tạo giỏ mới dành cho khách
    gio_hang = GioHang.objects.create(nguoi_dung=None)
    session['giohang_id'] = gio_hang.id
    return gio_hang


#  Thêm sản phẩm (cho cả khách và user)
def them_san_pham(gio_hang, san_pham_id, so_luong=1):
    # Kiểm tra nếu san_pham_id là object SanPham thì dùng trực tiếp, nếu không thì tìm theo ma_sp
    if isinstance(san_pham_id, SanPham): #cẩm sửa 3 dòng này
        san_pham = san_pham_id
    else:
        san_pham = SanPham.objects.get(ma_sp=san_pham_id)
    item, created = GioHangItem.objects.get_or_create(
        gio_hang=gio_hang,
        san_pham=san_pham
    )
    if not created:
        item.so_luong += so_luong
    else:
        item.so_luong = so_luong #cẩm sửa dòng này
    item.save()
    return item


#  Xóa 1 sản phẩm khỏi giỏ
def xoa_san_pham(gio_hang, item_id):
    GioHangItem.objects.filter(gio_hang=gio_hang, id=item_id).delete()


#  Xóa toàn bộ giỏ (sau khi đặt hàng)
def xoa_tat_ca(gio_hang):
    gio_hang.items.all().delete()
