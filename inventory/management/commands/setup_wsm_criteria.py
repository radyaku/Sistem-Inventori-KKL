"""
Management command untuk setup data awal WSM Criteria
Sesuai dengan Tabel 4.2 dari spesifikasi
"""
from django.core.management.base import BaseCommand
from inventory.models import WSMCriteria


class Command(BaseCommand):
    help = 'Setup default WSM Criteria berdasarkan Tabel 4.2'

    def handle(self, *args, **options):
        criteria_data = [
            {
                'code': 'C1',
                'name': 'Kondisi Layar',
                'description': 'Deadpixel, Whitespot, Scratch, Dent pada layar',
                'weight': 0.25,
                'attribute_type': 'benefit',
            },
            {
                'code': 'C2',
                'name': 'Kondisi Fisik',
                'description': 'Kemulusan casing, engsel patah, baut hilang, penyok',
                'weight': 0.20,
                'attribute_type': 'benefit',
            },
            {
                'code': 'C3',
                'name': 'Kesehatan Baterai',
                'description': 'Battery Health, status drop, ketersediaan unit',
                'weight': 0.15,
                'attribute_type': 'benefit',
            },
            {
                'code': 'C4',
                'name': 'Input Device',
                'description': 'Fungsi tombol keyboard, responsivitas touchpad',
                'weight': 0.15,
                'attribute_type': 'benefit',
            },
            {
                'code': 'C5',
                'name': 'Spesifikasi Teknis',
                'description': 'Kapasitas RAM, Tipe Storage (SSD/HDD), Prosesor, dan kondisi daya',
                'weight': 0.15,
                'attribute_type': 'benefit',
            },
            {
                'code': 'C6',
                'name': 'Konektivitas',
                'description': 'Port USB, HDMI, Audio Jack, Kamera, Speaker',
                'weight': 0.10,
                'attribute_type': 'benefit',
            },
        ]

        created_count = 0
        updated_count = 0

        for data in criteria_data:
            criteria, created = WSMCriteria.objects.update_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'weight': data['weight'],
                    'attribute_type': data['attribute_type'],
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {criteria.code} - {criteria.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated: {criteria.code} - {criteria.name}'))

        self.stdout.write(self.style.SUCCESS(f'\nTotal: {created_count} created, {updated_count} updated'))
