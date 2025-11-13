from django.urls import path
from . import views

app_name = 'Hotro'

urlpatterns = [
    path('', views.yeu_cau_cua_toi, name='trang_chu'),
    path('tao-yeu-cau/', views.tao_yeu_cau, name='tao_yeu_cau'),
    path('yeu-cau-cua-toi/', views.yeu_cau_cua_toi, name='yeu_cau_cua_toi'),
    path('chi-tiet/<int:pk>/', views.chi_tiet_yeu_cau, name='chi_tiet_yeu_cau'),

    # Người bán
    path('nguoi-ban/', views.bang_nguoi_ban, name='bang_nguoi_ban'),
    path('nguoi-ban/cap-nhat-trang-thai/<int:pk>/', views.doi_trang_thai, name='doi_trang_thai'),

    # Quản trị
    path('quan-tri/bang-dieu-khien/', views.bang_quan_tri, name='bang_quan_tri'),
]

