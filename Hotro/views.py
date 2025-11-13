from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib import messages
from .models import YeuCauHoTro, TinNhanHoTro, HoSoNguoiDung
from .forms import YeuCauHoTroForm, TinNhanHoTroForm


# ======= KIỂM TRA QUYỀN =======

def la_nguoi_ban(user):
    try:
        return user.ho_so.vai_tro == 'nguoi_ban'
    except:
        return False

def la_quan_tri(user):
    return user.is_staff


# ======= TẠO YÊU CẦU HỖ TRỢ =======

@login_required
def tao_yeu_cau(request):
    if request.method == 'POST':
        form = YeuCauHoTroForm(request.POST)
        if form.is_valid():
            yc = form.save(commit=False)
            yc.khach_hang = request.user
            yc.save()
            messages.success(request, "Yêu cầu của bạn đã được gửi.")
            return redirect('Hotro:yeu_cau_cua_toi')
    else:
        form = YeuCauHoTroForm()

    return render(request, 'Hotro/tao_yeu_cau.html', {'form': form})


# ======= DANH SÁCH YÊU CẦU CỦA NGƯỜI DÙNG =======

@login_required
def yeu_cau_cua_toi(request):
    danh_sach = YeuCauHoTro.objects.filter(khach_hang=request.user).order_by('-ngay_tao')
    return render(request, 'hotro/yeu_cau_cua_toi.html', {'danh_sach': danh_sach})


# ======= CHI TIẾT YÊU CẦU =======

@login_required
def chi_tiet_yeu_cau(request, pk):
    yc = get_object_or_404(YeuCauHoTro, pk=pk)

    # QUYỀN XEM:
    # - Khách hàng chỉ xem yêu cầu của mình
    # - Người bán xem yêu cầu được giao
    # - Quản trị được xem tất cả
    if request.user != yc.khach_hang and not request.user.is_staff and not la_nguoi_ban(request.user):
        if not (la_nguoi_ban(request.user) and yc.nguoi_ban == request.user):
            messages.error(request, "Bạn không có quyền xem yêu cầu này.")
            return redirect('Hotro:yeu_cau_cua_toi')

    # Gửi tin nhắn mới
    if request.method == 'POST':
        form = TinNhanHoTroForm(request.POST)
        if form.is_valid():
            tn = form.save(commit=False)
            tn.nguoi_gui = request.user
            tn.yeu_cau = yc
            tn.save()

            # cập nhật trạng thái tự động
            if yc.trang_thai == 'cho_xu_ly':
                yc.trang_thai = 'dang_xu_ly'
                yc.save(update_fields=['trang_thai'])

            return redirect(reverse('Hotro:chi_tiet_yeu_cau', args=[yc.pk]))

    else:
        form = TinNhanHoTroForm()

    return render(request, 'Hotro/chi_tiet.html', {'yeu_cau': yc, 'form': form})


# ======= DASHBOARD NGƯỜI BÁN =======

@login_required
@user_passes_test(la_nguoi_ban)
def bang_nguoi_ban(request):
    danh_sach = YeuCauHoTro.objects.all().order_by('-ngay_tao')
    return render(request, 'Hotro/bang_nguoi_ban.html', {'danh_sach': danh_sach})


# ======= DASHBOARD ADMIN =======

@login_required
@user_passes_test(la_quan_tri)
def bang_quan_tri(request):
    danh_sach = YeuCauHoTro.objects.all().order_by('-ngay_tao')
    return render(request, 'Hotro/bang_quan_tri.html', {'danh_sach': danh_sach})


# ======= THAY ĐỔI TRẠNG THÁI =======

@login_required
@user_passes_test(la_nguoi_ban)
def doi_trang_thai(request, pk):
    yc = get_object_or_404(YeuCauHoTro, pk=pk)

    if request.method == 'POST':
        trang_thai_moi = request.POST.get('trang_thai')
        if trang_thai_moi in dict(YeuCauHoTro.TRANG_THAI_LUA_CHON):
            yc.trang_thai = trang_thai_moi
            yc.nguoi_ban = request.user
            yc.save(update_fields=['trang_thai', 'nguoi_ban'])

            messages.success(request, "Đã cập nhật trạng thái.")

    return redirect('Hotro:bang_nguoi_ban')
