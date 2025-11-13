"""
URL configuration for Playzy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from Taikhoan import views as Taikhoan_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('muahang/', include('Muahang.urls')),
    path('khohang/', include('Khohang.urls')),
    path('sanpham/', include('Sanpham.urls')),
    path('Taikhoan/', include('Taikhoan.urls')),
    path('', views.home, name='home'),
    path('gioi-thieu/', views.gioi_thieu, name='gioi_thieu'),
    path('tin-tuc/', include('Tintuc.urls', namespace='Tintuc')),
    path('hotro/', include('Hotro.urls', namespace='Hotro')),
    path('baocao/', include('Baocao.urls', namespace='baocao')),
    path('lien-he/', include('Lienhe.urls', namespace='Lienhe')),
    path('chinh-sach-bao-mat/', views.chinh_sach_bao_mat, name='chinh_sach_bao_mat')
]

# Thêm dòng này để phục vụ file media (ảnh upload) khi ở chế độ DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)




