from django import forms
from Khohang.models import KhoHang
from Sanpham.models import SanPham

class ThemGiaoDichForm(forms.Form):
    CHOICES = [
        ('NHAP', 'Nhập kho (Từ NCC)'),
        ('XUAT', 'Xuất kho (Giao khách)'),
        ('DIEU_CHINH', 'Điều chỉnh (Kiểm kê, hỏng)'),
    ]

    ma_sp = forms.ModelChoiceField(
        queryset=SanPham.objects.all(),
        label="Chọn sản phẩm",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    loai_giao_dich = forms.ChoiceField(
        choices=CHOICES,
        label="Loại giao dịch",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    so_luong = forms.IntegerField(
        label="Số lượng thay đổi",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 1})
    )
    ghi_chu = forms.CharField(
        label="Ghi chú",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        loai = cleaned_data.get('loai_giao_dich')
        so_luong = cleaned_data.get('so_luong')
        san_pham = cleaned_data.get('ma_sp')

        if loai in {'NHAP', 'XUAT'}:
            if so_luong is None or so_luong <= 0:
                self.add_error('so_luong', "Số lượng phải lớn hơn 0 đối với giao dịch nhập/xuất.")
        elif loai == 'DIEU_CHINH':
            if so_luong is None or so_luong == 0:
                self.add_error('so_luong', "Số lượng điều chỉnh không được bằng 0.")

        if loai == 'XUAT' and san_pham and so_luong:
            kho = KhoHang.objects.filter(ma_sp=san_pham).first()
            if kho and so_luong > kho.so_luong_ton_kho:
                self.add_error('so_luong', f"Tồn kho hiện tại chỉ còn {kho.so_luong_ton_kho}.")

        return cleaned_data
