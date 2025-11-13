from django.shortcuts import render
from .models import CauHoiThuongGap

def xem_cau_hoi_view(request):
    danh_sach_cau_hoi = CauHoiThuongGap.objects.filter(hien_thi=True).order_by('-ngay_tao')
    return render(request, 'lienhe/cau_hoi.html', {'danh_sach_cau_hoi': danh_sach_cau_hoi})

