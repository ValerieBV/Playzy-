# san_pham/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg
from .models import SanPham, DanhMuc, HinhAnhSanPham, DanhGiaSanPham
from .forms import DanhGiaForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, DecimalField
from django.core.paginator import Paginator
from django.http import JsonResponse
import re


# ========== CÁC VIEW PUBLIC (CHO NGƯỜI DÙNG) ==========

def trang_danh_muc(request):
    """
    (Chức năng: Tìm kiếm & Lọc sản phẩm - ĐÃ THÊM SẮP XẾP)
    """
    danh_muc_list = DanhMuc.objects.all()
    # Bỏ order_by('ma_sp') ở đây, chúng ta sẽ quyết định ở cuối
    san_pham_list = SanPham.objects.filter(trang_thai='CON_HANG')

    # 1. Lọc Tìm kiếm
    query = request.GET.get('q', '')
    if query:
        san_pham_list = san_pham_list.filter(ten_sp__icontains=query)

    # 2. Lọc Danh mục
    danh_muc_slug = request.GET.get('danh_muc', '')
    selected_danh_muc = None
    if danh_muc_slug:
        try:
            selected_danh_muc = DanhMuc.objects.get(duong_dan=danh_muc_slug)
            san_pham_list = san_pham_list.filter(danh_muc=selected_danh_muc)
        except DanhMuc.DoesNotExist:
            pass

    # 3. Lọc Độ tuổi
    selected_ages = request.GET.getlist('age')
    if selected_ages:
        age_query = Q()
        if '6' in selected_ages: age_query |= Q(tuoi_tren_6=True)
        if '16' in selected_ages: age_query |= Q(tuoi_tren_16=True)
        if '18' in selected_ages: age_query |= Q(tuoi_tren_18=True)
        san_pham_list = san_pham_list.filter(age_query)

    # 4. Lọc Số người chơi
    selected_players = request.GET.getlist('players')
    if selected_players:
        player_query = Q()
        if '2' in selected_players: player_query |= Q(choi_2_nguoi=True)
        if '4' in selected_players: player_query |= Q(choi_4_nguoi=True)
        if 'tren_4' in selected_players: player_query |= Q(choi_tren_4_nguoi=True)
        san_pham_list = san_pham_list.filter(player_query)

    # 5. Lọc Giá (Bao gồm annotate 'gia_thuc_te')
    try:
        selected_price_min = int(request.GET.get('price_min', '0'))
    except ValueError:
        selected_price_min = 0
    try:
        selected_price_max = int(request.GET.get('price_max', '10000000'))
    except ValueError:
        selected_price_max = 10000000

    gia_moi_expression = ExpressionWrapper(
        F('gia_goc') * (1 - F('ty_le_giam_gia') / 100.0),
        output_field=DecimalField()
    )
    san_pham_list = san_pham_list.annotate(gia_thuc_te=gia_moi_expression)

    if selected_price_max != 10000000:
        san_pham_list = san_pham_list.filter(gia_thuc_te__lte=selected_price_max)
    if selected_price_min != 0:
        san_pham_list = san_pham_list.filter(gia_thuc_te__gte=selected_price_min)

    # ▼▼▼ (BẮT ĐẦU LOGIC SẮP XẾP MỚI) ▼▼▼
    sort_option = request.GET.get('sort', 'default')

    if sort_option == 'price-asc':
        # (Giá tăng dần -> LỚN nhất xuống NHỎ nhất -> Dấu trừ)
        # (Đã sửa: Đảo ngược logic)
        san_pham_list = san_pham_list.order_by('gia_thuc_te')
    elif sort_option == 'price-desc':
        # (Giá giảm dần -> NHỎ nhất lên LỚN nhất -> Không dấu)
        # (Đã sửa: Đảo ngược logic)
        san_pham_list = san_pham_list.order_by('-gia_thuc_te')
    elif sort_option == 'newest':
        san_pham_list = san_pham_list.order_by('-ngay_tao')
    else:
        # 'default'
        san_pham_list = san_pham_list.order_by('ma_sp')


    # 6. Logic Phân trang
    paginator = Paginator(san_pham_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 7. Lấy các tham số filter
    other_params = request.GET.copy()
    if 'page' in other_params:
        del other_params['page']
    other_params_url = other_params.urlencode()

    # 8. Tạo context
    context = {
        'danh_sach_san_pham': page_obj,
        'danh_sach_danh_muc': danh_muc_list,
        'selected_danh_muc': selected_danh_muc,
        'query': query,
        'selected_ages': selected_ages,
        'selected_players': selected_players,
        'selected_price_min': selected_price_min,
        'selected_price_max': selected_price_max,
        'other_params': other_params_url,

        'sort_option': sort_option,  # Gửi lựa chọn sắp xếp ra template
    }

    return render(request, 'Sanpham/trang_danh_muc.html', context)


def chi_tiet_san_pham(request, ma_sp):
    """
    (Chức năng: Xem chi tiết sản phẩm)
    """
    san_pham = get_object_or_404(SanPham, pk=ma_sp)
    hinh_anh_phu = san_pham.hinh_anh_phu.all()
    danh_gia_list = san_pham.danh_gia.all().order_by('-ngay_danh_gia')
    avg_rating = danh_gia_list.aggregate(Avg('diem_danh_gia'))['diem_danh_gia__avg']
    san_pham_lien_quan = san_pham.san_pham_lien_quan.all()
    if not san_pham_lien_quan.exists():
        san_pham_lien_quan = SanPham.objects.filter(
            danh_muc=san_pham.danh_muc
        ).exclude(pk=ma_sp)[:3]
    
    # Kiểm tra xem người dùng đã đánh giá chưa
    user_review = None
    if request.user.is_authenticated:
        user_review = DanhGiaSanPham.objects.filter(
            ma_sp=san_pham,
            ma_nguoi_dung=request.user
        ).first()
    
    # Form đánh giá
    danh_gia_form = DanhGiaForm()
    if user_review:
        danh_gia_form = DanhGiaForm(instance=user_review)
    
    context = {
        'san_pham': san_pham,
        'hinh_anh_phu': hinh_anh_phu,
        'danh_gia_list': danh_gia_list,
        'avg_rating': avg_rating or 0,
        'san_pham_lien_quan': san_pham_lien_quan,
        'danh_gia_form': danh_gia_form,
        'user_review': user_review,
    }
    return render(request, 'Sanpham/chi_tiet_san_pham.html', context)


@login_required
def them_danh_gia(request, ma_sp):
    """
    Thêm hoặc cập nhật đánh giá sản phẩm
    """
    san_pham = get_object_or_404(SanPham, pk=ma_sp)
    
    # Kiểm tra xem người dùng đã đánh giá chưa
    user_review = DanhGiaSanPham.objects.filter(
        ma_sp=san_pham,
        ma_nguoi_dung=request.user
    ).first()
    
    if request.method == 'POST':
        if user_review:
            # Cập nhật đánh giá cũ
            form = DanhGiaForm(request.POST, instance=user_review)
        else:
            # Tạo đánh giá mới
            form = DanhGiaForm(request.POST)
        
        if form.is_valid():
            danh_gia = form.save(commit=False)
            danh_gia.ma_sp = san_pham
            danh_gia.ma_nguoi_dung = request.user
            
            if not user_review:
                # Tạo mã đánh giá mới
                danh_gia.ma_danh_gia = form.generate_ma_danh_gia()
            
            danh_gia.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Trả về JSON nếu là AJAX request
                return JsonResponse({
                    'status': 'success',
                    'message': 'Cảm ơn bạn đã đánh giá sản phẩm!'
                })
            else:
                messages.success(request, 'Cảm ơn bạn đã đánh giá sản phẩm!')
                return redirect('Sanpham:chi_tiet_san_pham', ma_sp=ma_sp)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Vui lòng điền đầy đủ thông tin đánh giá.'
                })
            else:
                messages.error(request, 'Vui lòng điền đầy đủ thông tin đánh giá.')
                return redirect('Sanpham:chi_tiet_san_pham', ma_sp=ma_sp)
    
    return redirect('Sanpham:chi_tiet_san_pham', ma_sp=ma_sp)

# --- (ĐÃ XÓA CÁC VIEW QUẢN LÝ TÙY CHỈNH) ---
# (Vì chúng ta đã dùng /admin/ của Jazzmin)