from django.urls import path
from . import views

urlpatterns = [
    path('dang-ky/', views.dang_ky, name='dangky'),
    path('dang-nhap/', views.dang_nhap, name='dangnhap'),
    path('dang-xuat/', views.dang_xuat, name='dangxuat'),
    path('trangchu/', views.trang_chu, name='trangchu'),
    path('thong-tin-ca-nhan/', views.thong_tin_ca_nhan, name='thong_tin_ca_nhan'),
]