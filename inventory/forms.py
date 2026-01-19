from django import forms
from .models import Laptop, Assessment, WSMCriteria


class LaptopForm(forms.ModelForm):
    """Form untuk create/edit Laptop"""
    
    class Meta:
        model = Laptop
        fields = [
            'asset_code', 'serial_number', 'brand', 'model',
            'processor', 'ram_gb', 'storage_type', 'storage_size_gb',
            'gpu', 'last_user', 'open_price'
        ]
        widgets = {
            'asset_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: AST-001'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nomor serial'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Lenovo, Dell, HP'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: ThinkPad X1 Carbon Gen 9'
            }),
            'processor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Core i7'
            }),
            'ram_gb': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '8, 16, 32...'
            }),
            'storage_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'storage_size_gb': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '256, 512, 1024...'
            }),
            'gpu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opsional: NVIDIA GeForce...'
            }),
            'last_user': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama user terakhir'
            }),
            'open_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Harga pembukaan (Rp)'
            }),
        }


class AssessmentForm(forms.ModelForm):
    """Form untuk input penilaian WSM"""
    
    laptop_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan kode aset',
            'list': 'laptop-list'
        }),
        label='Kode Aset'
    )
    
    class Meta:
        model = Assessment
        fields = [
            'screen_condition', 'physical_condition', 'battery_health',
            'keyboard_status', 'touchpad_status', 'specs_score',
            'power_status', 'connectivity_score',
            'camera_ok', 'speaker_ok', 'usb_port_ok',
            'hinge_broken', 'screw_missing', 'dent_crack',
            'condition_notes'
        ]
        widgets = {
            'screen_condition': forms.Select(attrs={'class': 'form-select'}),
            'physical_condition': forms.Select(attrs={'class': 'form-select'}),
            'battery_health': forms.Select(attrs={'class': 'form-select'}),
            'keyboard_status': forms.Select(attrs={'class': 'form-select'}),
            'touchpad_status': forms.Select(attrs={'class': 'form-select'}),
            'specs_score': forms.Select(attrs={'class': 'form-select'}),
            'power_status': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'connectivity_score': forms.Select(attrs={'class': 'form-select'}),
            'camera_ok': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'speaker_ok': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'usb_port_ok': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'hinge_broken': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'screw_missing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dent_crack': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'condition_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Catatan tambahan tentang kondisi aset...'
            }),
        }


class WSMCriteriaForm(forms.ModelForm):
    """Form untuk manage kriteria WSM"""
    
    class Meta:
        model = WSMCriteria
        fields = ['code', 'name', 'description', 'weight', 'attribute_type', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'C1, C2, C3...'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama kriteria'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Deskripsi kriteria...'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '1',
                'placeholder': '0.00 - 1.00'
            }),
            'attribute_type': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StatusChangeForm(forms.Form):
    """Form untuk mengubah status laptop"""
    
    STATUS_CHOICES = [
        ('ready', 'Tersedia'),
        ('auction', 'Proses Lelang'),
        ('sold', 'Terjual'),
        ('used', 'Dipakai'),
        ('scrapped', 'Dibuang'),
    ]
    
    new_status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Status Baru'
    )
    sold_price = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Harga jual (wajib jika status Terjual)'
        }),
        label='Harga Jual'
    )
    buyer_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nama pembeli (wajib jika status Terjual)'
        }),
        label='Nama Pembeli'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_status = cleaned_data.get('new_status')
        sold_price = cleaned_data.get('sold_price')
        buyer_name = cleaned_data.get('buyer_name')
        
        if new_status == 'sold':
            if not sold_price:
                self.add_error('sold_price', 'Harga jual wajib diisi untuk status Terjual.')
            if not buyer_name:
                self.add_error('buyer_name', 'Nama pembeli wajib diisi untuk status Terjual.')
        
        return cleaned_data
