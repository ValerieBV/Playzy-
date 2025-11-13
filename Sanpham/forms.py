# Sanpham/forms.py

from django import forms
from .models import DanhGiaSanPham
import string
import random


class DanhGiaForm(forms.ModelForm):
    diem_danh_gia = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Đánh giá',
        required=True
    )
    
    binh_luan = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Nhập đánh giá của bạn về sản phẩm này...'
        }),
        label='Bình luận',
        required=False,
        max_length=1000
    )
    
    class Meta:
        model = DanhGiaSanPham
        fields = ['diem_danh_gia', 'binh_luan']
    
    def generate_ma_danh_gia(self):
        """Tạo mã đánh giá ngẫu nhiên"""
        while True:
            ma = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not DanhGiaSanPham.objects.filter(ma_danh_gia=ma).exists():
                return ma
