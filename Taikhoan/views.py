from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from .models import NguoiDung
import re


# ------------------ TRANG ĐĂNG KÝ ------------------
def dang_ky(request):
    # Nếu đã đăng nhập, redirect về trang chủ
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Kiểm tra các trường bắt buộc
        if not username or not email or not password or not password2:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin.')
            return redirect('dangky')

        # Kiểm tra độ dài username
        if len(username) < 3:
            messages.error(request, 'Tên đăng nhập phải có ít nhất 3 ký tự.')
            return redirect('dangky')

        # Kiểm tra định dạng email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messages.error(request, 'Sai định dạng email. Mời nhập lại.')
            return redirect('dangky')

        # Kiểm tra độ dài mật khẩu
        if len(password) < 6:
            messages.error(request, 'Mật khẩu phải có ít nhất 6 ký tự.')
            return redirect('dangky')

        # Kiểm tra trùng mật khẩu
        if password != password2:
            messages.error(request, 'Mật khẩu không khớp. Mời nhập lại.')
            return redirect('dangky')

        # Kiểm tra tài khoản tồn tại
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại. Mời chọn tên khác.')
            return redirect('dangky')

        # Kiểm tra email đã được sử dụng
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email này đã được sử dụng. Mời sử dụng email khác.')
            return redirect('dangky')

        # Tạo tài khoản mới
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Đăng ký tài khoản thành công! Vui lòng đăng nhập.')
            return redirect('dangnhap')
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra khi đăng ký: {str(e)}')
            return redirect('dangky')

    return render(request, 'Taikhoan/dang_ky.html')


# ------------------ TRANG ĐĂNG NHẬP ------------------
def dang_nhap(request):
    # Nếu đã đăng nhập, redirect về trang chủ
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Kiểm tra các trường bắt buộc
        if not username or not password:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin đăng nhập.')
            return redirect('dangnhap')

        # Xác thực thông tin người dùng
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Chào mừng {user.username} quay trở lại!')
            # Nếu là admin hoặc staff → chuyển sang trang quản trị
            if user.is_superuser or user.is_staff:
                return redirect('/admin/')
            # Nếu là người dùng thường → về trang chủ
            else:
                # Kiểm tra xem có next parameter không (redirect sau khi login)
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, 'Tên tài khoản hoặc mật khẩu không đúng, vui lòng thử lại.')
            return redirect('dangnhap')

    return render(request, 'Taikhoan/dang_nhap.html')


# ------------------ TRANG ĐĂNG XUẤT ------------------
def dang_xuat(request):
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất khỏi hệ thống. Cảm ơn bạn đã sử dụng Playzy.')
    return redirect('dangnhap')


# ------------------ TRANG CHỦ ------------------
def trang_chu(request):
    return render(request, 'home.html')


# ------------------ TRANG THÔNG TIN CÁ NHÂN ------------------
@login_required
def thong_tin_ca_nhan(request):
    user = request.user
    nguoidung, created = NguoiDung.objects.get_or_create(user=user)

    if request.method == 'POST':
        ho_ten = request.POST.get('ho_ten')
        sdt = request.POST.get('so_dien_thoai')
        dia_chi = request.POST.get('dia_chi')
        ngay_sinh_raw = request.POST.get('ngay_sinh')

        # Xử lý định dạng ngày
        ngay_sinh = None
        if ngay_sinh_raw:
            try:
                if "/" in ngay_sinh_raw:
                    ngay_sinh = datetime.strptime(ngay_sinh_raw, "%d/%m/%Y").date()
                else:
                    ngay_sinh = datetime.strptime(ngay_sinh_raw, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Ngày sinh không hợp lệ. Định dạng: DD/MM/YYYY hoặc YYYY-MM-DD")
                return redirect('thong_tin_ca_nhan')

        # Cập nhật thông tin
        nguoidung.ho_ten = ho_ten
        nguoidung.sdt = sdt
        nguoidung.dia_chi = dia_chi
        nguoidung.ngay_sinh = ngay_sinh
        nguoidung.save()

        messages.success(request, "Thông tin của bạn đã được cập nhật thành công.")
        return redirect('thong_tin_ca_nhan')

    return render(request, 'Taikhoan/thong_tin_ca_nhan.html', {'nguoidung': nguoidung, 'user': user})

# ------------------ TRANG LỊCH SỬ MUA HÀNG ------------------




