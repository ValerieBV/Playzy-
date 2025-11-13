# Muahang/urls.py
from django.urls import path
from . import views

app_name = 'Muahang'

urlpatterns = [
    # Giỏ hàng
    path('gio-hang/', views.giohang_view, name='giohang'),
    path('gio-hang/xoa/<int:item_id>/', views.xoa_khoi_giohang, name='xoa_khoi_giohang'),
    path('gio-hang/cap-nhat-so-luong/<int:item_id>/', views.update_quantity, name='update_quantity'),
    path('gio-hang/mini/', views.mini_cart_view, name='mini_cart'),
    path('gio-hang/mini-page/', views.mini_cart_page, name='mini_cart_page'),
    path("them-gio-hang/<str:ma_sp>/", views.them_gio_hang, name="them_gio_hang"),
    path("mua-ngay/<str:ma_sp>/", views.mua_ngay, name="mua_ngay"),


    # Đặt hàng
    path('dat-hang/', views.dat_hang, name='dat_hang'),
    # Theo dõi đơn hàng
    path('theo-doi-don-hang/', views.theo_doi_don_hang, name='theo_doi_don_hang'),
    path('chi-tiet-don-hang/<int:don_hang_id>/', views.chi_tiet_don_hang, name='chi_tiet_don_hang'),
    path('thanh-toan-qr/<int:don_hang_id>/', views.thanh_toan_qr, name='thanh_toan_qr'),
    path('xac-nhan-thanh-toan/<int:don_hang_id>/', views.xac_nhan_thanh_toan, name='xac_nhan_thanh_toan'),

    # Trang kết quả giao hàng
    path('don-hang/<int:donhang_id>/<str:trang_thai>/', views.ket_qua_giao_hang, name='ket_qua_giao_hang'),
]