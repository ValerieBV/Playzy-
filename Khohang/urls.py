from django.urls import path
from . import views
app_name = 'Khohang'

urlpatterns = [
    # Link: /khohang/
    path('', views.chi_tiet_kho_hang_view, name='chi_tiet_kho_hang'),

    # Link: /khohang/lich-su-giao-dich/
    path('lich-su-giao-dich/', views.lich_su_giao_dich_view, name='lich_su_giao_dich'),

    # Link: /khohang/them-giao-dich/
    path('them-giao-dich/', views.them_giao_dich_view, name='them_giao_dich'),
]
