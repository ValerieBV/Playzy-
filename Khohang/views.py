from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import KhoHang, LichSuGiaoDich
from Sanpham.models import SanPham, DanhMuc
from Muahang.models import DonHang
from .forms import ThemGiaoDichForm, ThemSanPhamVaoKhoForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin import site

@transaction.atomic
def dieu_chinh_kho_logic(ma_san_pham: str,
                         so_luong: int,
                         loai_giao_dich: str,
                         ghi_chu: str,
                         don_hang: DonHang = None):
    """
    Hàm xử lý nhập, xuất, điều chỉnh kho.
    Tự động tạo bản ghi kho nếu sản phẩm chưa có trong kho.
    """
    try:
        san_pham = get_object_or_404(SanPham, pk=ma_san_pham)

        # Tự tạo kho nếu chưa có
        kho_hang, created = KhoHang.objects.select_for_update().get_or_create(ma_sp=san_pham)

        so_luong_thay_doi = so_luong

        if loai_giao_dich == 'NHAP':
            if so_luong <= 0:
                return (False, "Số lượng 'Nhập kho' phải là số dương.")
            kho_hang.so_luong_ton_kho = F('so_luong_ton_kho') + so_luong

        elif loai_giao_dich == 'XUAT':
            if so_luong <= 0:
                return (False, "Số lượng 'Xuất kho' phải là số dương.")
            if kho_hang.so_luong_ton_kho < so_luong:
                return (False, f"Không đủ tồn kho cho {san_pham.ten_sp}.")
            kho_hang.so_luong_ton_kho = F('so_luong_ton_kho') - so_luong
            so_luong_thay_doi = -so_luong

        elif loai_giao_dich == 'DIEU_CHINH':
            if kho_hang.so_luong_ton_kho + so_luong < 0:
                return (False, "Điều chỉnh làm tồn kho âm. Vui lòng kiểm tra lại.")
            kho_hang.so_luong_ton_kho = F('so_luong_ton_kho') + so_luong
        else:
            return (False, "Loại giao dịch không hợp lệ.")

        # Lưu lại kết quả kho
        kho_hang.save()
        kho_hang.refresh_from_db()

        # Ghi lại lịch sử giao dịch
        LichSuGiaoDich.objects.create(
            ma_sp=san_pham,
            don_hang=don_hang,
            loai_giao_dich=loai_giao_dich,
            so_luong_thay_doi=so_luong_thay_doi,
            thoi_gian_thuc_hien=None,  # auto_add sẽ xử lý
            ghi_chu=ghi_chu
        )

        return (True, "Cập nhật kho thành công.")

    except SanPham.DoesNotExist:
        return (False, f"Sản phẩm {ma_san_pham} không tồn tại.")
    except Exception as e:
        return (False, f"Lỗi hệ thống: {str(e)}")


# Kiểm tra quyền admin
def is_admin(user):
    return user.is_staff


@staff_member_required
def chi_tiet_kho_hang_view(request):
    ma_sp = request.GET.get('ma_sp')
    ten_sp = request.GET.get('ten_sp')
    danh_muc = request.GET.get('danh_muc')
    tu_gia = request.GET.get('tu_gia')
    den_gia = request.GET.get('den_gia')
    
    # Lấy danh sách sản phẩm chưa có trong kho để hiển thị trong dropdown
    san_pham_trong_kho_ids = set(KhoHang.objects.values_list('ma_sp_id', flat=True))
    san_pham_chua_co_kho_queryset = SanPham.objects.exclude(ma_sp__in=san_pham_trong_kho_ids)
    san_pham_chua_co_kho_list = list(san_pham_chua_co_kho_queryset)
    
    # Xử lý POST request để thêm sản phẩm vào kho
    if request.method == 'POST' and 'them_san_pham' in request.POST:
        ma_sp = request.POST.get('ma_sp')
        so_luong = request.POST.get('so_luong_ton_kho')
        
        if ma_sp and so_luong:
            try:
                san_pham = SanPham.objects.get(ma_sp=ma_sp)
                so_luong = int(so_luong)
                
                # Kiểm tra lại để tránh duplicate
                if not KhoHang.objects.filter(ma_sp=san_pham).exists():
                    # Tạo kho hàng mới, model sẽ tự động tạo mã kho hàng unique
                    kho_hang = KhoHang(ma_sp=san_pham, so_luong_ton_kho=so_luong)
                    kho_hang.save()
                    messages.success(request, f'Đã thêm sản phẩm {san_pham.ten_sp} vào kho hàng với số lượng {so_luong}.')
                    return redirect('Khohang:chi_tiet_kho_hang')
                else:
                    messages.error(request, f'Sản phẩm {san_pham.ten_sp} đã có trong kho hàng.')
            except SanPham.DoesNotExist:
                messages.error(request, 'Sản phẩm không tồn tại.')
            except ValueError:
                messages.error(request, 'Số lượng không hợp lệ.')
            except Exception as e:
                error_msg = str(e)
                if 'UNIQUE constraint' in error_msg or 'unique' in error_msg.lower():
                    messages.error(request, f'Lỗi: Mã kho hàng bị trùng. Vui lòng thử lại.')
                else:
                    messages.error(request, f'Lỗi khi thêm sản phẩm: {error_msg}')
        else:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin.')

    danh_sach_ton_kho = KhoHang.objects.select_related('ma_sp', 'ma_sp__danh_muc').all()

    if ma_sp:
        danh_sach_ton_kho = danh_sach_ton_kho.filter(ma_sp__ma_sp__icontains=ma_sp)
    if ten_sp:
        danh_sach_ton_kho = danh_sach_ton_kho.filter(ma_sp__ten_sp__icontains=ten_sp)
    if danh_muc:
        danh_sach_ton_kho = danh_sach_ton_kho.filter(ma_sp__danh_muc__ma_danh_muc=danh_muc)
    if tu_gia:
        danh_sach_ton_kho = danh_sach_ton_kho.filter(ma_sp__gia_goc__gte=tu_gia)
    if den_gia:
        danh_sach_ton_kho = danh_sach_ton_kho.filter(ma_sp__gia_goc__lte=den_gia)
    
    context = {
        **site.each_context(request),  # ← thêm dòng này để sidebar/header Jazzmin hiện
        'title': 'Chi tiết kho hàng',
        'danh_sach_ton_kho': danh_sach_ton_kho,
        'danh_muc_list': DanhMuc.objects.all(),
        'selected_danh_muc': danh_muc or '',
        'san_pham_chua_co_kho': san_pham_chua_co_kho_list,
    }
    return render(request, 'kho_hang/chi_tiet_kho_hang.html', context)


@staff_member_required
def lich_su_giao_dich_view(request):
    qs = LichSuGiaoDich.objects.select_related('ma_sp').all()

    loai = request.GET.get('loai_giao_dich')
    ma = request.GET.get('ma_giao_dich')
    tu = request.GET.get('tu_ngay')
    den = request.GET.get('den_ngay')

    if ma:
        qs = qs.filter(ma_giao_dich__icontains=ma)
    if loai:
        qs = qs.filter(loai_giao_dich=loai)
    if tu:
        qs = qs.filter(thoi_gian_thuc_hien__gte=tu)
    if den:
        qs = qs.filter(thoi_gian_thuc_hien__lte=den)

    context = {
        **site.each_context(request),
        'title': 'Lịch sử giao dịch',
        'lich_su_giao_dich': qs,
    }
    return render(request, 'kho_hang/lich_su_giao_dich.html', context)



@staff_member_required
def them_giao_dich_view(request):
    if request.method == 'POST':
        form = ThemGiaoDichForm(request.POST)
        if form.is_valid():
            san_pham = form.cleaned_data['ma_sp']
            loai_gd = form.cleaned_data['loai_giao_dich']
            so_luong = form.cleaned_data['so_luong']
            ghi_chu = form.cleaned_data['ghi_chu']

            so_luong_thay_doi = so_luong if loai_gd != 'XUAT' else -so_luong

            LichSuGiaoDich.objects.create(
                ma_sp=san_pham,
                loai_giao_dich=loai_gd,
                so_luong_thay_doi=so_luong_thay_doi,
                ghi_chu=ghi_chu
            )
            messages.success(request, "Giao dịch đã được lưu và cập nhật tồn kho.")
            return redirect('Khohang:lich_su_giao_dich')
        else:
            messages.error(request, "Dữ liệu không hợp lệ. Vui lòng kiểm tra lại các trường được đánh dấu.")
    else:
        form = ThemGiaoDichForm()
    return render(request, 'kho_hang/them_giao_dich.html', {'form': form})
