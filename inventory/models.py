from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Laptop(models.Model):
    """Model untuk menyimpan data laptop/aset"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('assessed', 'Sudah Dinilai'),
        ('ready', 'Tersedia'),
        ('auction', 'Proses Lelang'),
        ('sold', 'Terjual'),
        ('used', 'Dipakai'),
        ('scrapped', 'Dibuang'),
    ]
    
    PHYSICAL_GRADE_CHOICES = [
        ('A', 'Grade A'),
        ('B', 'Grade B'),
        ('C', 'Grade C'),
        ('D', 'Grade D'),
    ]
    
    STORAGE_TYPE_CHOICES = [
        ('SSD', 'SSD'),
        ('HDD', 'HDD'),
        ('NVME', 'NVMe SSD'),
    ]
    
    # Identifikasi
    asset_code = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name='Kode Aset'
    )
    serial_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='Nomor Serial'
    )
    
    # Spesifikasi
    brand = models.CharField(max_length=50, verbose_name='Merk')
    model = models.CharField(max_length=100, verbose_name='Model')
    processor = models.CharField(max_length=100, verbose_name='Prosesor')
    ram_gb = models.PositiveIntegerField(verbose_name='RAM (GB)')
    storage_type = models.CharField(
        max_length=10, 
        choices=STORAGE_TYPE_CHOICES, 
        default='SSD',
        verbose_name='Tipe Storage'
    )
    storage_size_gb = models.PositiveIntegerField(verbose_name='Ukuran Storage (GB)')
    gpu = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='GPU'
    )
    
    # Status & Grade
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name='Status'
    )
    physical_grade = models.CharField(
        max_length=1, 
        choices=PHYSICAL_GRADE_CHOICES,
        blank=True,
        null=True,
        verbose_name='Grade Fisik'
    )
    
    # Finansial
    open_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Harga Pembukaan'
    )
    sold_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Harga Jual'
    )
    buyer_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Nama Pembeli'
    )
    
    # User terakhir
    last_user = models.CharField(
        max_length=100, 
        verbose_name='User Terakhir'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Dibuat')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Diperbarui')
    
    class Meta:
        verbose_name = 'Laptop'
        verbose_name_plural = 'Laptop'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.asset_code} - {self.brand} {self.model}"
    
    def get_specs_display(self):
        """Return formatted specs string"""
        return f"{self.processor} / {self.ram_gb}GB / {self.storage_size_gb}GB {self.storage_type}"


class WSMCriteria(models.Model):
    """Kriteria penilaian WSM dengan bobot"""
    
    ATTRIBUTE_TYPE_CHOICES = [
        ('benefit', 'Benefit'),  # Semakin tinggi semakin baik
        ('cost', 'Cost'),        # Semakin rendah semakin baik
    ]
    
    code = models.CharField(max_length=10, unique=True, verbose_name='Kode')
    name = models.CharField(max_length=100, verbose_name='Nama Kriteria')
    description = models.TextField(blank=True, verbose_name='Deskripsi')
    weight = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='Bobot'
    )
    attribute_type = models.CharField(
        max_length=10, 
        choices=ATTRIBUTE_TYPE_CHOICES,
        default='benefit',
        verbose_name='Tipe Atribut'
    )
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    
    class Meta:
        verbose_name = 'Kriteria WSM'
        verbose_name_plural = 'Kriteria WSM'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name} (Bobot: {self.weight})"


class Assessment(models.Model):
    """Penilaian kondisi laptop menggunakan WSM"""
    
    SCREEN_CONDITION_CHOICES = [
        (5, 'Sangat Baik - Tidak ada cacat'),
        (4, 'Baik - Cacat minimal tidak terlihat'),
        (3, 'Cukup - Ada 1-2 titik whitespot'),
        (2, 'Kurang - Lecet kasar/deadpixel banyak'),
        (1, 'Rusak - Layar pecah/retak'),
    ]
    
    BATTERY_HEALTH_CHOICES = [
        (5, 'Sangat Baik - >2 jam'),
        (4, 'Baik - 1-2 jam'),
        (3, 'Cukup - 30 menit - 1 jam'),
        (2, 'Kurang - <30 menit'),
        (1, 'Rusak - Perlu service/mati'),
    ]
    
    KEYBOARD_STATUS_CHOICES = [
        (5, 'Normal - Semua tombol berfungsi'),
        (4, 'Baik - Bekas pemakaian minimal'),
        (3, 'Cukup - Ada tombol agak keras'),
        (2, 'Kurang - Ada tombol error'),
        (1, 'Rusak - Tidak berfungsi'),
    ]
    
    TOUCHPAD_STATUS_CHOICES = [
        (5, 'Normal - Responsif sempurna'),
        (4, 'Baik - Bekas pemakaian minimal'),
        (3, 'Cukup - Agak kurang responsif'),
        (2, 'Kurang - Sering error'),
        (1, 'Rusak - Tidak berfungsi'),
    ]
    
    PHYSICAL_CONDITION_CHOICES = [
        (5, 'Sangat Baik - Mulus seperti baru'),
        (4, 'Baik - Bekas pemakaian minimal'),
        (3, 'Cukup - Ada goresan halus'),
        (2, 'Kurang - Penyok/retak halus'),
        (1, 'Rusak - Rusak parah'),
    ]
    
    SPECS_SCORE_CHOICES = [
        (5, 'Sangat Baik - High-end specs'),
        (4, 'Baik - Mid-high specs'),
        (3, 'Cukup - Mid specs'),
        (2, 'Kurang - Entry-level'),
        (1, 'Rusak - Outdated'),
    ]
    
    CONNECTIVITY_CHOICES = [
        (5, 'Sangat Baik - Semua port berfungsi'),
        (4, 'Baik - 1 port minor tidak berfungsi'),
        (3, 'Cukup - 2 port tidak berfungsi'),
        (2, 'Kurang - Port utama bermasalah'),
        (1, 'Rusak - Mayoritas port rusak'),
    ]
    
    laptop = models.OneToOneField(
        Laptop, 
        on_delete=models.CASCADE, 
        related_name='assessment',
        verbose_name='Laptop'
    )
    
    # C1 - Kondisi Layar (0.25)
    screen_condition = models.IntegerField(
        choices=SCREEN_CONDITION_CHOICES,
        verbose_name='C1 - Kondisi Layar'
    )
    
    # C2 - Kondisi Fisik (0.20)
    physical_condition = models.IntegerField(
        choices=PHYSICAL_CONDITION_CHOICES,
        verbose_name='C2 - Kondisi Fisik'
    )
    
    # C3 - Kesehatan Baterai (0.15)
    battery_health = models.IntegerField(
        choices=BATTERY_HEALTH_CHOICES,
        verbose_name='C3 - Kesehatan Baterai'
    )
    
    # C4 - Input Device (0.15)
    keyboard_status = models.IntegerField(
        choices=KEYBOARD_STATUS_CHOICES,
        verbose_name='C4a - Keyboard'
    )
    touchpad_status = models.IntegerField(
        choices=TOUCHPAD_STATUS_CHOICES,
        verbose_name='C4b - Touchpad'
    )
    
    # C5 - Spesifikasi Teknis (0.15)
    specs_score = models.IntegerField(
        choices=SPECS_SCORE_CHOICES,
        verbose_name='C5 - Spesifikasi Teknis'
    )
    power_status = models.BooleanField(
        default=True, 
        verbose_name='Kondisi Daya Hidup'
    )
    
    # C6 - Konektivitas (0.10)
    connectivity_score = models.IntegerField(
        choices=CONNECTIVITY_CHOICES,
        verbose_name='C6 - Konektivitas'
    )
    camera_ok = models.BooleanField(default=True, verbose_name='Kamera OK')
    speaker_ok = models.BooleanField(default=True, verbose_name='Speaker OK')
    usb_port_ok = models.BooleanField(default=True, verbose_name='Port USB OK')
    
    # Kerusakan Fisik (checklist)
    hinge_broken = models.BooleanField(default=False, verbose_name='Engsel Rusak')
    screw_missing = models.BooleanField(default=False, verbose_name='Baut Hilang')
    dent_crack = models.BooleanField(default=False, verbose_name='Penyok/Retak')
    
    # Hasil kalkulasi
    wsm_score = models.FloatField(null=True, blank=True, verbose_name='Skor WSM')
    final_grade = models.CharField(
        max_length=1, 
        null=True, 
        blank=True,
        verbose_name='Grade Akhir'
    )
    condition_notes = models.TextField(
        blank=True, 
        verbose_name='Catatan Kondisi'
    )
    
    assessed_at = models.DateTimeField(auto_now=True, verbose_name='Tanggal Penilaian')
    assessed_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Dinilai Oleh'
    )
    
    class Meta:
        verbose_name = 'Penilaian'
        verbose_name_plural = 'Penilaian'
    
    def __str__(self):
        return f"Assessment {self.laptop.asset_code} - Grade {self.final_grade}"
    
    def get_condition_tags(self):
        """Return list of condition issues"""
        tags = []
        if self.screen_condition <= 3:
            tags.append(dict(self.SCREEN_CONDITION_CHOICES).get(self.screen_condition, ''))
        if self.battery_health <= 3:
            tags.append('Baterai Lemah')
        if self.keyboard_status <= 3:
            tags.append('Keyboard Aus')
        if self.touchpad_status <= 3:
            tags.append('Touchpad Rusak')
        if self.hinge_broken:
            tags.append('Engsel Rusak')
        if self.dent_crack:
            tags.append('Penyok/Retak')
        if not tags:
            tags.append('Kondisi Baik')
        return tags


class AuditLog(models.Model):
    """Log aktivitas sistem"""
    
    ACTION_CHOICES = [
        ('create', 'Buat'),
        ('update', 'Update'),
        ('delete', 'Hapus'),
        ('assess', 'Penilaian'),
        ('status_change', 'Ubah Status'),
    ]
    
    user = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Pengguna'
    )
    action = models.CharField(
        max_length=20, 
        choices=ACTION_CHOICES,
        verbose_name='Aksi'
    )
    model_name = models.CharField(max_length=50, verbose_name='Model')
    object_id = models.CharField(max_length=50, verbose_name='ID Objek')
    object_repr = models.CharField(max_length=200, verbose_name='Deskripsi')
    changes = models.JSONField(null=True, blank=True, verbose_name='Perubahan')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Waktu')
    
    class Meta:
        verbose_name = 'Log Audit'
        verbose_name_plural = 'Log Audit'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.object_repr}"
