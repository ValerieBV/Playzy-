# muahang/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GioHang, GioHangItem, DonHang, DonHangItem, TrangThaiDonHang
from .forms import DonDatHangForm
from .cart import lay_gio_hang, them_san_pham, xoa_san_pham, xoa_tat_ca
from django.template.loader import render_to_string
from Sanpham.models import SanPham  # cẩm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST  # Thêm import này - cẩm
from decimal import Decimal  # Thêm import Decimal
import qrcode
import qrcode.image.pil
import io
import random
import string
import base64


# Giả lập voucher tự động do cửa hàng áp dụng
def lay_voucher_tu_cua_hang(user):
    """
    Giả lập voucher tự động của cửa hàng.
    Nếu tổng giỏ > 500k thì giảm 5%.
    """
    giohang = lay_gio_hang(user)
    tong = giohang.tong_tien()
    if tong > Decimal('500000'):
        so_tien_giam = tong * Decimal('0.05')  # Sửa: Dùng Decimal thay vì float
        return {
            'ma': 'AUTO5%',  # admin áp dụng tự động
            'so_tien_giam': so_tien_giam
        }
    return None


@login_required
def dat_hang(request):
    giohang = lay_gio_hang(request.user)

    if not giohang.items.exists():
        return redirect('Muahang:trang_danh_muc')  # cam sua

    # Lấy voucher tự động (nếu có)
    voucher = lay_voucher_tu_cua_hang(request.user)
    giam_gia = voucher['so_tien_giam'] if voucher else 0
    ma_voucher = voucher['ma'] if voucher else ''

    # Phí vận chuyển cố định
    phi_van_chuyen = 30_000

    # Tổng thanh toán cuối, đã trừ giảm giá tự động
    tong_thanh_toan = giohang.tong_tien() + phi_van_chuyen - giam_gia

    if request.method == 'POST':
        form = DonDatHangForm(request.POST)
        if form.is_valid():
            donhang = form.save(commit=False)
            donhang.nguoi_dung = request.user
            donhang.tong_tien = giohang.tong_tien()
            donhang.phi_van_chuyen = phi_van_chuyen
            donhang.so_tien_duoc_giam = giam_gia
            donhang.trang_thai = "cho_xac_nhan"

            # Lấy phương thức thanh toán khách chọn
            donhang.payment_method = request.POST.get('payment_method', 'COD')

            donhang.save()

            # Tạo DonHangItem từ giỏ hàng
            for item in giohang.items.all():
                DonHangItem.objects.create(
                    don_hang=donhang,
                    san_pham=item.san_pham,
                    so_luong=item.so_luong,
                    gia=item.san_pham.gia_da_giam  # <-- Sửa: Dùng giá đã giảm
                )

            # Xóa giỏ hàng sau khi đặt
            xoa_tat_ca(giohang)

            # Nếu là thanh toán online (MoMo, ZaloPay, VNPay), chuyển đến trang QR code
            if donhang.payment_method in ['MOMO', 'ZALOPAY', 'VNPAY']:
                return redirect('Muahang:thanh_toan_qr', don_hang_id=donhang.id)
            
            # Nếu là COD, chuyển đến trang theo dõi đơn hàng
            return redirect('Muahang:theo_doi_don_hang')
    else:
        form = DonDatHangForm()

    # Danh sách phương thức thanh toán
    payment_methods = [
        ('COD', 'Thanh toán khi nhận hàng', 'cod_icon.png'),
        ('VNPAY', 'Thẻ ATM / Credit / Debit', 'vnpay_logo.png'),
        ('ZALOPAY', 'Ví ZaloPay', 'zalopay_logo.png'),
        ('MOMO', 'Ví MoMo', 'momo_logo.png'),
    ]

    context = {
        'form': form,
        'giohang': giohang,
        'phi_van_chuyen': phi_van_chuyen,
        'giam_gia': giam_gia,
        'ma_voucher': ma_voucher,
        'tong_thanh_toan': tong_thanh_toan,
        'selected_payment_method': request.POST.get('payment_method', None),  # Lấy từ POST nếu có
        'payment_methods': payment_methods,
        'show_promo': bool(voucher),
    }

    return render(request, 'Muahang/dat_hang.html', context)


def mini_cart_view(request):
    giohang = lay_gio_hang(request.user if request.user.is_authenticated else request.session)
    items = giohang.items.all()

    # Cẩm đã sửa - Tính số tiền còn thiếu để được freeship
    tong_tien = float(giohang.tong_tien())
    freeship_threshold = 100000
    con_thieu = max(0, freeship_threshold - tong_tien)

    # Cẩm đã sửa - render partial HTML cho dropdown (thay đổi từ mini_cart_content.html sang mini_cart_dropdown.html)
    html = render_to_string('Muahang/mini_cart_dropdown.html', {
        'giohang': giohang,
        'items': items,
        'con_thieu': con_thieu,  # Cẩm đã sửa - thêm biến con_thieu
    }, request=request)

    return JsonResponse({'html': html})


def mini_cart_page(request):
    """View để hiển thị mini_cart_content.html như một trang đầy đủ"""
    giohang = lay_gio_hang(request.user if request.user.is_authenticated else request.session)
    items = giohang.items.all()

    context = {
        'giohang': giohang,
        'items': items,
    }

    return render(request, 'Muahang/mini_cart_content.html', context)


# khách xem gi hàng không cần đăng nhập
# muahang/views.py
def giohang_view(request):
    # Lấy giỏ hàng cho user hoặc khách
    giohang = lay_gio_hang(request.user if request.user.is_authenticated else request.session)
    items = giohang.items.all()  # danh sách sản phẩm trong giỏ

    # Nếu giỏ trống → hiển thị trang trống
    if not items.exists():
        return render(request, 'Muahang/gio_hang_trong.html')

    # Nếu có sản phẩm → hiển thị trang có sản phẩm
    context = {
        'giohang': giohang,
        'items': items,
        'tong_tien': giohang.tong_tien(),
    }
    return render(request, 'Muahang/gio_hang_co_san_pham.html', context)


# def them_giohang(request, sanpham_id):
#    #thêm sản phẩm vào giỏ hàng
#     giohang = lay_gio_hang(request.user if request.user.is_authenticated else request.session)
#     them_san_pham(giohang, sanpham_id)
#     return redirect('muahang:giohang')
# xóa đi vì có code thêm giỏ hàng mới dưới rồi

def xoa_khoi_giohang(request, item_id):
    # xóa sản phẩm khỏi giỏ hàng
    giohang = lay_gio_hang(request.user if request.user.is_authenticated else request.session)
    xoa_san_pham(giohang, item_id)
    return redirect('Muahang:giohang')


def update_quantity(request, item_id):
    """Cập nhật số lượng sản phẩm trong giỏ hàng (tăng/giảm)"""
    giohang = lay_gio_hang(request.user if request.user.is_authenticated else request.session)

    try:
        item = GioHangItem.objects.get(id=item_id, gio_hang=giohang)
    except GioHangItem.DoesNotExist:
        # Cẩm đã sửa - hỗ trợ AJAX request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({'status': 'error', 'message': 'Sản phẩm không tồn tại'}, status=404)
        return redirect('Muahang:mini_cart_page')

    action = request.POST.get('action')
    item_was_deleted = False

    if action == 'increase':
        item.so_luong += 1
        item.save()
    elif action == 'decrease':
        item.so_luong -= 1
        if item.so_luong <= 0:
            item_id_before_delete = item.id
            item.delete()
            item_was_deleted = True
        else:
            item.save()

    # Cẩm đã sửa - Nếu là AJAX request, trả về JSON thay vì redirect
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # Tính lại giỏ hàng sau khi cập nhật
        giohang.refresh_from_db()
        
        # Lấy thông tin item sau khi cập nhật (nếu item vẫn còn)
        item_data = None
        if not item_was_deleted:
            try:
                # Reload item từ database
                item = GioHangItem.objects.get(id=item.id, gio_hang=giohang)
                item_data = {
                    'id': item.id,
                    'quantity': item.so_luong,
                    'item_total': float(item.thanh_tien())
                }
            except GioHangItem.DoesNotExist:
                pass
        
        return JsonResponse({
            'status': 'success',
            'total_items': giohang.tong_so_luong(),
            'total_price': float(giohang.tong_tien()),
            'item': item_data,  # Thông tin item đã cập nhật (None nếu đã xóa)
            'item_deleted': item_was_deleted  # Flag để biết item có bị xóa không
        })

    return redirect('Muahang:mini_cart_page')


# theo dõi đơn hàng
@login_required
def theo_doi_don_hang(request):
    tat_ca = DonHang.objects.filter(nguoi_dung=request.user)

    cho_xac_nhan = tat_ca.filter(trang_thai="cho_xac_nhan")
    da_xac_nhan = tat_ca.filter(trang_thai="da_xac_nhan")
    dang_giao = tat_ca.filter(trang_thai="dang_giao")
    da_giao = tat_ca.filter(trang_thai="da_giao")
    thanh_cong = tat_ca.filter(trang_thai="thanh_cong")
    that_bai = tat_ca.filter(trang_thai="that_bai")

    return render(request, "Muahang/theo_doi_don_hang.html", {
        "tat_ca": tat_ca,
        "cho_xac_nhan": cho_xac_nhan,
        "da_xac_nhan": da_xac_nhan,
        "dang_giao": dang_giao,
        "da_giao": da_giao,
        "thanh_cong": thanh_cong,
        "that_bai": that_bai
    })



# chi tiết đơn hàng
@login_required
def chi_tiet_don_hang(request, don_hang_id):
    don_hang = get_object_or_404(DonHang, id=don_hang_id, nguoi_dung=request.user)
    
    # Lấy lịch sử trạng thái đơn hàng
    lich_su_trang_thai = don_hang.lich_su_trang_thai.all().order_by('-thoi_gian')
    
    return render(request, 'Muahang/chi_tiet_don_hang.html', {
        'don_hang': don_hang,
        'lich_su_trang_thai': lich_su_trang_thai,
    })


# thanh toán QR code (demo)
@login_required
def thanh_toan_qr(request, don_hang_id):
    don_hang = get_object_or_404(DonHang, id=don_hang_id, nguoi_dung=request.user)
    
    # Tạo mã QR ngẫu nhiên (demo)
    # Tạo một chuỗi ngẫu nhiên để làm nội dung QR code
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
    qr_content = f"DEMO-{don_hang.payment_method}-{don_hang.id}-{random_string}"
    
    # Tạo QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)
    
    # Tạo ảnh QR code
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Lưu vào buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Chuyển đổi thành base64 để hiển thị trong template
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Tên phương thức thanh toán
    payment_names = {
        'MOMO': 'Ví MoMo',
        'ZALOPAY': 'Ví ZaloPay',
        'VNPAY': 'VNPay',
    }
    
    context = {
        'don_hang': don_hang,
        'qr_image': qr_image_base64,
        'payment_name': payment_names.get(don_hang.payment_method, 'Thanh toán online'),
        'tong_thanh_toan': don_hang.tong_thanh_toan(),
    }
    
    return render(request, 'Muahang/thanh_toan_qr.html', context)


# xác nhận thanh toán (demo)
@login_required
@require_POST
def xac_nhan_thanh_toan(request, don_hang_id):
    don_hang = get_object_or_404(DonHang, id=don_hang_id, nguoi_dung=request.user)
    
    # Cập nhật trạng thái đơn hàng thành "Chờ xác nhận" (hoặc có thể là "Đang giao" nếu muốn)
    don_hang.trang_thai = 'cho_xac_nhan'
    don_hang.save()
    
    # Tạo lịch sử trạng thái
    TrangThaiDonHang.objects.create(
        don_hang=don_hang,
        noi_dung='Cho xac nhan'
    )
    
    return redirect('Muahang:theo_doi_don_hang')


# trạng thái đơn
@login_required
def ket_qua_giao_hang(request, donhang_id, trang_thai):
    # giao thành công hay thất bại
    don_hang = get_object_or_404(DonHang, id=donhang_id, nguoi_dung=request.user)

    # Ghi trạng thái mới nếu chưa có
    noi_dung = trang_thai.replace('-', ' ').title()
    if not TrangThaiDonHang.objects.filter(don_hang=don_hang, noi_dung=noi_dung).exists():
        TrangThaiDonHang.objects.create(don_hang=don_hang, noi_dung=noi_dung)

    return render(request, 'Muahang/trang_thai_don_hang.html', {
        'don_hang': don_hang,
        'trang_thai': trang_thai,
    })


# # danh sách sản phẩm
# def sanpham_view(request):
#     sanphams = SanPham.objects.all()
#     return render(request, 'Muahang/sanpham.html', {'sanphams': sanphams})
# Nên xóa hàm trên vì đã có app SanPham

# --- THÊM GIỎ HÀNG (NÚT "THÊM GIỎ HÀNG") ---
def them_gio_hang(request, ma_sp):
    giohang = lay_gio_hang(request.user if request.user.is_authenticated else request.session)

    # BƯỚC 1: LẤY ĐỐI TƯỢNG SẢN PHẨM TỪ ma_sp
    try:
        san_pham = SanPham.objects.get(ma_sp=ma_sp)
    except SanPham.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Sản phẩm không tồn tại.",
        }, status=404)

    try:
        so_luong = int(request.GET.get('qty', 1))
        if so_luong < 1:
            so_luong = 1
    except ValueError:
        so_luong = 1

    # BƯỚC 2: TRUYỀN ĐỐI TƯỢNG SẢN PHẨM (không phải ma_sp)
    them_san_pham(giohang, san_pham, so_luong)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "status": "success",
            "message": "Đã thêm sản phẩm vào giỏ",
            "total_items": giohang.tong_so_luong(),
        })

    return redirect(request.META.get("HTTP_REFERER", "/"))


# --- MUA NGAY (NÚT "MUA NGAY") ---
def mua_ngay(request, ma_sp):
    giohang = lay_gio_hang(request.user if request.user.is_authenticated else request.session)

    # BƯỚC 1: LẤY ĐỐI TƯỢNG SẢN PHẨM TỪ ma_sp
    try:
        san_pham = SanPham.objects.get(ma_sp=ma_sp)
    except SanPham.DoesNotExist:
        return redirect("/")

    try:
        so_luong = int(request.GET.get('qty', 1))
        if so_luong < 1:
            so_luong = 1
    except ValueError:
        so_luong = 1

    xoa_tat_ca(giohang)

    # BƯỚC 2: TRUYỀN ĐỐI TƯỢNG SẢN PHẨM (không phải ma_sp)
    them_san_pham(giohang, san_pham, so_luong)

    return redirect("Muahang:dat_hang")