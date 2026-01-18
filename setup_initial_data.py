"""
Script untuk setup data awal:
1. Create superuser admin
2. Create default WSM Criteria
3. Create dummy laptop data

Run: python manage.py shell < setup_initial_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from inventory.models import Laptop, WSMCriteria, Assessment
from inventory.services.wsm_calculator import process_assessment

User = get_user_model()

# 1. Create admin user
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@protelindo.com',
        password='admin123',
        role='admin',
        first_name='Kepala Aset IT'
    )
    print(f'Admin user created: {admin.username}')
else:
    print('Admin user already exists')

# 2. Create WSM Criteria (Tabel 4.2)
criteria_data = [
    {'code': 'C1', 'name': 'Kondisi Layar', 'description': 'Deadpixel, Whitespot, Scratch, Dent pada layar', 'weight': 0.25},
    {'code': 'C2', 'name': 'Kondisi Fisik', 'description': 'Kemulusan casing, engsel patah, baut hilang, penyok', 'weight': 0.20},
    {'code': 'C3', 'name': 'Kesehatan Baterai', 'description': 'Battery Health, status drop, ketersediaan unit', 'weight': 0.15},
    {'code': 'C4', 'name': 'Input Device', 'description': 'Fungsi tombol keyboard, responsivitas touchpad', 'weight': 0.15},
    {'code': 'C5', 'name': 'Spesifikasi Teknis', 'description': 'Kapasitas RAM, Tipe Storage, Prosesor, kondisi daya', 'weight': 0.15},
    {'code': 'C6', 'name': 'Konektivitas', 'description': 'Port USB, HDMI, Audio Jack, Kamera, Speaker', 'weight': 0.10},
]

for data in criteria_data:
    obj, created = WSMCriteria.objects.update_or_create(
        code=data['code'],
        defaults={'name': data['name'], 'description': data['description'], 'weight': data['weight'], 'attribute_type': 'benefit', 'is_active': True}
    )
    print(f'{"Created" if created else "Updated"}: {obj.code} - {obj.name}')

# 3. Create dummy laptop data
dummy_laptops = [
    {'asset_code': 'AST-001', 'serial_number': 'SN1234567890', 'brand': 'Lenovo', 'model': 'ThinkPad X1 Carbon Gen 9', 'processor': 'Core i7', 'ram_gb': 16, 'storage_size_gb': 512, 'last_user': 'Ahmad Rizki'},
    {'asset_code': 'AST-002', 'serial_number': 'SN0987654321', 'brand': 'Dell', 'model': 'Latitude 7420', 'processor': 'Core i5', 'ram_gb': 8, 'storage_size_gb': 256, 'last_user': 'Siti Nurhaliza'},
    {'asset_code': 'AST-003', 'serial_number': 'SN1122334455', 'brand': 'HP', 'model': 'EliteBook 840 G8', 'processor': 'Core i5', 'ram_gb': 8, 'storage_size_gb': 256, 'last_user': 'Budi Santoso'},
    {'asset_code': 'AST-004', 'serial_number': 'SN5566778899', 'brand': 'Lenovo', 'model': 'ThinkPad T14', 'processor': 'Core i5', 'ram_gb': 16, 'storage_size_gb': 512, 'last_user': 'Dewi Lestari'},
    {'asset_code': 'AST-005', 'serial_number': 'SN9988776655', 'brand': 'Dell', 'model': 'Inspiron 15 3000', 'processor': 'Core i3', 'ram_gb': 4, 'storage_size_gb': 128, 'last_user': 'Eko Prasetyo'},
    {'asset_code': 'AST-006', 'serial_number': 'SN4433221100', 'brand': 'Apple', 'model': 'MacBook Air M1', 'processor': 'Apple M1', 'ram_gb': 8, 'storage_size_gb': 256, 'last_user': 'Fitri Handayani'},
    {'asset_code': 'AST-007', 'serial_number': 'SN7788990011', 'brand': 'Asus', 'model': 'VivoBook 15', 'processor': 'Core i5', 'ram_gb': 8, 'storage_size_gb': 512, 'last_user': 'Gunawan Wijaya'},
    {'asset_code': 'AST-008', 'serial_number': 'SN1357924680', 'brand': 'HP', 'model': 'ProBook 450 G7', 'processor': 'Core i5', 'ram_gb': 8, 'storage_size_gb': 256, 'last_user': 'Asshidiq Jafar'},
]

for data in dummy_laptops:
    obj, created = Laptop.objects.update_or_create(
        asset_code=data['asset_code'],
        defaults={
            'serial_number': data['serial_number'],
            'brand': data['brand'],
            'model': data['model'],
            'processor': data['processor'],
            'ram_gb': data['ram_gb'],
            'storage_type': 'SSD',
            'storage_size_gb': data['storage_size_gb'],
            'last_user': data['last_user'],
            'status': 'draft',
        }
    )
    print(f'{"Created" if created else "Updated"} laptop: {obj.asset_code}')

# 4. Create sample assessments
admin_user = User.objects.get(username='admin')
sample_assessments = [
    {'asset_code': 'AST-001', 'screen': 4, 'physical': 4, 'battery': 5, 'keyboard': 4, 'touchpad': 5, 'specs': 5, 'connectivity': 5},
    {'asset_code': 'AST-002', 'screen': 3, 'physical': 3, 'battery': 3, 'keyboard': 4, 'touchpad': 4, 'specs': 3, 'connectivity': 4},
    {'asset_code': 'AST-003', 'screen': 4, 'physical': 4, 'battery': 4, 'keyboard': 4, 'touchpad': 4, 'specs': 4, 'connectivity': 5},
    {'asset_code': 'AST-004', 'screen': 3, 'physical': 3, 'battery': 4, 'keyboard': 3, 'touchpad': 3, 'specs': 4, 'connectivity': 4},
    {'asset_code': 'AST-005', 'screen': 2, 'physical': 1, 'battery': 1, 'keyboard': 2, 'touchpad': 1, 'specs': 2, 'connectivity': 2},
    {'asset_code': 'AST-006', 'screen': 5, 'physical': 5, 'battery': 5, 'keyboard': 5, 'touchpad': 5, 'specs': 5, 'connectivity': 5},
]

for data in sample_assessments:
    laptop = Laptop.objects.get(asset_code=data['asset_code'])
    assessment, created = Assessment.objects.update_or_create(
        laptop=laptop,
        defaults={
            'screen_condition': data['screen'],
            'physical_condition': data['physical'],
            'battery_health': data['battery'],
            'keyboard_status': data['keyboard'],
            'touchpad_status': data['touchpad'],
            'specs_score': data['specs'],
            'connectivity_score': data['connectivity'],
            'power_status': True,
            'camera_ok': True,
            'speaker_ok': True,
            'usb_port_ok': True,
            'assessed_by': admin_user,
        }
    )
    # Calculate WSM
    assessment = process_assessment(assessment, save=True)
    print(f'Assessment for {laptop.asset_code}: Score={assessment.wsm_score}, Grade={assessment.final_grade}')

print('\n=== Setup Complete ===')
print(f'Admin login: admin / admin123')
print(f'Laptops: {Laptop.objects.count()}')
print(f'Criteria: {WSMCriteria.objects.count()}')
print(f'Assessments: {Assessment.objects.count()}')
