from django.urls import path
from . import views

app_name = "baocao"

urlpatterns = [
    path("", views.danh_sach_bao_cao, name="list"),
    path("<int:pk>/", views.baocao_detail, name="detail"),
    path("<int:pk>/delete/", views.baocao_delete, name="delete"),

    # Báo cáo doanh thu
    path("doanhthu/", views.baocao_doanhthu, name="doanhthu"),
    path("api/doanhthu/", views.baocao_doanhthu_api, name="doanhthu_api"),
]
