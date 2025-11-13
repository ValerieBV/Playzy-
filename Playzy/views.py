from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Sanpham.models import SanPham
from Tintuc.models import BaiViet

def home(request):
    # CHO PHÉP TRUY CẬP TRANG CHỦ KHÔNG CẦN ĐĂNG NHẬP
    # Chỉ yêu cầu đăng nhập khi thêm giỏ hàng hoặc mua hàng
    latest_products = SanPham.objects.filter(trang_thai='CON_HANG').order_by('-ngay_tao')[:5]
    latest_posts = BaiViet.objects.all().order_by('-ngay_dang')[:5]
    context = {
        'latest_products': latest_products,
        'latest_posts': latest_posts,
    }
    return render(request, 'home.html', context)

def gioi_thieu(request):
    return render(request, 'gioi_thieu.html')
def chinh_sach_bao_mat(request):
    return render(request, 'chinh_sach_bao_mat.html')