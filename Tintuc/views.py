from django.shortcuts import render, get_object_or_404
from .models import BaiViet

def trang_tintuc(request):
    baiviets = BaiViet.objects.all().order_by('-ngay_dang')
    bai_noi_bat = baiviets.first()
    danh_sach_bai_khac = baiviets[1:6] if bai_noi_bat else []
    return render(
        request,
        'Tintuc/tin_tuc.html',
        {
            'bai_noi_bat': bai_noi_bat,
            'danh_sach_bai_khac': danh_sach_bai_khac,
            'baiviets': baiviets,  # Truyền toàn bộ danh sách bài viết
        }
    )

def tin_tuc_chi_tiet(request, pk):
    bai_viet = get_object_or_404(BaiViet, pk=pk)
    bai_lien_quan = BaiViet.objects.exclude(pk=pk).order_by('-ngay_dang')[:5]
    return render(
        request,
        'Tintuc/tin_tuc_chi_tiet.html',
        {
            'bai_viet': bai_viet,
            'bai_lien_quan': bai_lien_quan,
        }
    )
