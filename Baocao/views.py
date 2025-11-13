from django.shortcuts import render, get_object_or_404, redirect
from .models import BaoCao
from django.http import JsonResponse
from django.db.models import Sum
from Muahang.models import DonHang, DonHangItem


# ✅ Danh sách báo cáo
def danh_sach_bao_cao(request):
    baocaos = BaoCao.objects.all()
    return render(request, "baocao/danh_sach_bao_cao.html", {"baocaos": baocaos})


# ✅ Chi tiết báo cáo
def baocao_detail(request, pk):
    bc = get_object_or_404(BaoCao, pk=pk)
    return render(request, "baocao/baocao_detail.html", {"bc": bc})


# ✅ Xóa báo cáo
def baocao_delete(request, pk):
    bc = get_object_or_404(BaoCao, pk=pk)
    bc.delete()
    return redirect("baocao:list")


# ✅ Trang báo cáo doanh thu
def baocao_doanhthu(request):
    return render(request, "baocao/baocao_doanhthu.html")


# ✅ API doanh thu cho Chart.js
def baocao_doanhthu_api(request):
    data = (
        DonHang.objects
        .values("ngay_dat__month")
        .annotate(tong=Sum("tong_tien"))
        .order_by("ngay_dat__month")
    )

    labels = [f"Tháng {d['ngay_dat__month']}" for d in data]
    values = [float(d["tong"]) for d in data]

    return JsonResponse({
        "labels": labels,
        "values": values
    })



