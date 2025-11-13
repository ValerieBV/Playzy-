#!/usr/bin/env python
"""
Script tạo các tài khoản mẫu để test
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Playzy.settings')
django.setup()

from django.contrib.auth.models import User

# Danh sách tài khoản mẫu
sample_users = [
    {
        'username': 'admin',
        'email': 'admin@playzy.com',
        'password': 'admin123',
        'is_superuser': True,
        'is_staff': True,
    },
    {
        'username': 'nguoidung1',
        'email': 'user1@playzy.com',
        'password': 'user123',
        'is_superuser': False,
        'is_staff': False,
    },
    {
        'username': 'nguoidung2',
        'email': 'user2@playzy.com',
        'password': 'user123',
        'is_superuser': False,
        'is_staff': False,
    },
    {
        'username': 'test',
        'email': 'test@playzy.com',
        'password': 'test123',
        'is_superuser': False,
        'is_staff': False,
    },
]

print("=" * 60)
print("TAO TAI KHOAN MAU")
print("=" * 60)

created_count = 0
existing_count = 0

for user_data in sample_users:
    username = user_data['username']
    
    # Kiểm tra xem user đã tồn tại chưa
    if User.objects.filter(username=username).exists():
        print(f"[!] Tai khoan '{username}' da ton tai, bo qua...")
        existing_count += 1
        continue
    
    # Tạo user mới
    try:
        user = User.objects.create_user(
            username=username,
            email=user_data['email'],
            password=user_data['password'],
        )
        user.is_superuser = user_data['is_superuser']
        user.is_staff = user_data['is_staff']
        user.save()
        
        user_type = "Admin" if user_data['is_superuser'] else "Nguoi dung"
        print(f"[OK] Da tao tai khoan: {username} ({user_type})")
        created_count += 1
    except Exception as e:
        print(f"[ERROR] Loi khi tao tai khoan '{username}': {str(e)}")

print("\n" + "=" * 60)
print(f"Ket qua: {created_count} tai khoan moi duoc tao, {existing_count} tai khoan da ton tai")
print("=" * 60)

if created_count > 0:
    print("\nDANH SACH TAI KHOAN DE DANG NHAP:")
    print("-" * 60)
    for user_data in sample_users:
        user_type = "Admin" if user_data['is_superuser'] else "Nguoi dung"
        print(f"Username: {user_data['username']:<20} Password: {user_data['password']:<10} ({user_type})")
    print("=" * 60)

