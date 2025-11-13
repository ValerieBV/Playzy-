from django.urls import path
from . import views

app_name = 'Tintuc'

urlpatterns = [
    path('', views.trang_tintuc, name='trang_tintuc'),
    path('<int:pk>/', views.tin_tuc_chi_tiet, name='chi_tiet'),
]
