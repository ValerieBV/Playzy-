from django.urls import path
from . import views

app_name = 'Lienhe'

urlpatterns = [
    path('', views.xem_cau_hoi_view, name='cau_hoi'),
]
