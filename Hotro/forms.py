from django import forms
from .models import YeuCauHoTro, TinNhanHoTro


class YeuCauHoTroForm(forms.ModelForm):
    class Meta:
        model = YeuCauHoTro
        fields = ['ten_san_pham', 'loai_yeu_cau', 'tieu_de', 'noi_dung']

        widgets = {
            'tieu_de': forms.TextInput(attrs={'class': 'form-control'}),
            'ten_san_pham': forms.TextInput(attrs={'class': 'form-control'}),
            'loai_yeu_cau': forms.Select(attrs={'class': 'form-control'}),
            'noi_dung': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class TinNhanHoTroForm(forms.ModelForm):
    class Meta:
        model = TinNhanHoTro
        fields = ['noi_dung']
        widgets = {
            'noi_dung': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Nhập tin nhắn...'
            }),
        }

