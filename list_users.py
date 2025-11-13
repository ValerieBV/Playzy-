#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Playzy.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 60)
print("DANH SACH TAI KHOAN TRONG HE THONG")
print("=" * 60)

users = User.objects.all().order_by('id')

if users.exists():
    print(f"\nTong so tai khoan: {users.count()}\n")
    print(f"{'STT':<5} {'Username':<20} {'Email':<30} {'Superuser':<10} {'Staff':<10}")
    print("-" * 80)
    
    for i, user in enumerate(users, 1):
        superuser = "Co" if user.is_superuser else "Khong"
        staff = "Co" if user.is_staff else "Khong"
        email = user.email if user.email else "(chua co)"
        print(f"{i:<5} {user.username:<20} {email:<30} {superuser:<10} {staff:<10}")
    
    print("\n" + "=" * 60)
    print("THONG TIN DANG NHAP:")
    print("=" * 60)
    print("\nDe dang nhap, su dung thong tin sau:\n")
    for i, user in enumerate(users, 1):
        print(f"{i}. Username: {user.username}")
        if user.email:
            print(f"   Email: {user.email}")
        print(f"   Loai: {'Admin' if user.is_superuser else 'Nguoi dung'}")
        print()
else:
    print("\nChua co tai khoan nao trong database!")
    print("\nBan co the:")
    print("1. Tao tai khoan qua trang dang ky: http://127.0.0.1:8000/Taikhoan/dang-ky/")
    print("2. Tao superuser: python manage.py createsuperuser")
    print("3. Chay script tao tai khoan mau: python create_sample_users.py")

print("=" * 60)

