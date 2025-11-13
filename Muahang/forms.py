# muahang/forms.py
from django import forms

from .models import DonHang


# Đơn đặt hàng
class DonDatHangForm(forms.ModelForm):
    class Meta:
        model = DonHang
        fields = ['ho_ten', 'so_dien_thoai', 'email', 'tinh', 'phuong_xa', 'dia_chi', 'ghi_chu']
        labels = {
            'ho_ten': 'Họ tên',
            'so_dien_thoai': 'Số điện thoại',
            'email': 'Email',
            'tinh' : 'Tỉnh',
            'phuong_xa':'Phường/ Xã',
            'dia_chi': 'Địa chỉ',
            'ghi_chu': 'Ghi chú ',
  }
        widgets = {
            'ho_ten': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ tên'}),
            'so_dien_thoai': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số điện thoại'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Nhập email'}),
            'tinh': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tỉnh/Thành phố'}),
            'phuong_xa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phường/Xã'}),
            'dia_chi': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Địa chỉ nhận hàng'}),
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ghi chú thêm (nếu có)'}),
        }