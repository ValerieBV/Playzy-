# Sanpham/urls.py

from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = 'Sanpham'

urlpatterns = [
    # URLs Public
    path('danh-muc/', views.trang_danh_muc, name='trang_danh_muc'),
    path('', RedirectView.as_view(pattern_name='Sanpham:trang_danh_muc', permanent=False)),
    path('san-pham/<str:ma_sp>/', views.chi_tiet_san_pham, name='chi_tiet_san_pham'),
    path('san-pham/<str:ma_sp>/danh-gia/', views.them_danh_gia, name='them_danh_gia'),

]
