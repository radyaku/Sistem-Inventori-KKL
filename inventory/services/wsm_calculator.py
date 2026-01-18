"""
WSM Calculator - Weighted Sum Model untuk penilaian aset laptop

Kriteria dan Bobot (dari Tabel 4.2):
- C1: Kondisi Layar (0.25)
- C2: Kondisi Fisik (0.20)
- C3: Kesehatan Baterai (0.15)
- C4: Input Device (0.15)
- C5: Spesifikasi Teknis (0.15)
- C6: Konektivitas (0.10)

Rubrik Skala (dari Tabel 4.3):
- 5: Sangat Baik (Excellent)
- 4: Baik (Good)
- 3: Cukup (Fair)
- 2: Kurang (Poor)
- 1: Rusak (Bad/Scrap)

Konversi Grade (dari Tabel 4.4):
- Grade A: 4.50 < V <= 5.00 (Excellent/Like New)
- Grade B: 3.50 < V <= 4.50 (Good/Standard)
- Grade C: 2.00 < V <= 3.50 (Fair/Minor Defect)
- Grade D: V <= 2.00 (Scrap/Salvage)
"""

# Default weights from Tabel 4.2
DEFAULT_WEIGHTS = {
    'C1': 0.25,  # Kondisi Layar
    'C2': 0.20,  # Kondisi Fisik
    'C3': 0.15,  # Kesehatan Baterai
    'C4': 0.15,  # Input Device
    'C5': 0.15,  # Spesifikasi Teknis
    'C6': 0.10,  # Konektivitas
}


def get_weights():
    """
    Ambil bobot dari database jika ada, 
    jika tidak gunakan default weights
    """
    from inventory.models import WSMCriteria
    
    weights = {}
    criteria = WSMCriteria.objects.filter(is_active=True)
    
    if criteria.exists():
        for c in criteria:
            weights[c.code] = c.weight
    else:
        weights = DEFAULT_WEIGHTS.copy()
    
    return weights


def calculate_input_device_score(keyboard_score, touchpad_score):
    """
    Hitung skor C4 - Input Device
    Rata-rata dari keyboard dan touchpad
    """
    return (keyboard_score + touchpad_score) / 2


def calculate_wsm_score(assessment):
    """
    Hitung skor WSM berdasarkan assessment
    
    Formula WSM:
    V = Σ(wj * xij)
    
    Di mana:
    - V = Skor akhir
    - wj = Bobot kriteria j
    - xij = Nilai alternatif i pada kriteria j
    
    Returns:
        tuple: (wsm_score, final_grade, condition_notes)
    """
    weights = get_weights()
    
    # Ambil nilai dari assessment
    c1_score = assessment.screen_condition  # Kondisi Layar
    c2_score = assessment.physical_condition  # Kondisi Fisik
    c3_score = assessment.battery_health  # Kesehatan Baterai
    c4_score = calculate_input_device_score(
        assessment.keyboard_status, 
        assessment.touchpad_status
    )  # Input Device
    c5_score = assessment.specs_score  # Spesifikasi Teknis
    c6_score = assessment.connectivity_score  # Konektivitas
    
    # Penalti untuk kondisi khusus
    penalty = 0
    condition_notes = []
    
    # Jika power status mati, beri penalti besar
    if not assessment.power_status:
        penalty += 1.0
        condition_notes.append("Tidak Menyala")
    
    # Kerusakan fisik
    if assessment.hinge_broken:
        penalty += 0.3
        condition_notes.append("Engsel Rusak")
    if assessment.screw_missing:
        penalty += 0.1
        condition_notes.append("Baut Hilang")
    if assessment.dent_crack:
        penalty += 0.2
        condition_notes.append("Penyok/Retak")
    
    # Konektivitas issues
    if not assessment.camera_ok:
        penalty += 0.1
        condition_notes.append("Kamera Rusak")
    if not assessment.speaker_ok:
        penalty += 0.1
        condition_notes.append("Speaker Rusak")
    if not assessment.usb_port_ok:
        penalty += 0.15
        condition_notes.append("Port USB Rusak")
    
    # Hitung WSM Score
    wsm_score = (
        weights.get('C1', 0.25) * c1_score +
        weights.get('C2', 0.20) * c2_score +
        weights.get('C3', 0.15) * c3_score +
        weights.get('C4', 0.15) * c4_score +
        weights.get('C5', 0.15) * c5_score +
        weights.get('C6', 0.10) * c6_score
    )
    
    # Apply penalty
    wsm_score = max(1.0, wsm_score - penalty)
    
    # Round to 2 decimal places
    wsm_score = round(wsm_score, 2)
    
    # Determine grade based on Tabel 4.4
    final_grade = determine_grade(wsm_score)
    
    # Generate condition notes
    if not condition_notes:
        if wsm_score >= 4.5:
            condition_notes.append("Sangat Baik")
        elif wsm_score >= 3.5:
            condition_notes.append("Kondisi Baik")
        elif wsm_score >= 2.0:
            condition_notes.append("Kondisi Cukup")
        else:
            condition_notes.append("Perlu Perbaikan")
    
    return wsm_score, final_grade, ", ".join(condition_notes)


def determine_grade(score):
    """
    Tentukan grade berdasarkan skor WSM (Tabel 4.4)
    
    - Grade A: 4.50 < V <= 5.00
    - Grade B: 3.50 < V <= 4.50
    - Grade C: 2.00 < V <= 3.50
    - Grade D: V <= 2.00
    """
    if score > 4.50:
        return 'A'
    elif score > 3.50:
        return 'B'
    elif score > 2.00:
        return 'C'
    else:
        return 'D'


def process_assessment(assessment, save=True):
    """
    Proses assessment dan update hasil WSM
    
    Args:
        assessment: Assessment object
        save: Boolean, jika True akan save ke database
        
    Returns:
        Assessment object dengan results
    """
    wsm_score, final_grade, condition_notes = calculate_wsm_score(assessment)
    
    assessment.wsm_score = wsm_score
    assessment.final_grade = final_grade
    assessment.condition_notes = condition_notes
    
    if save:
        assessment.save()
        
        # Update laptop status dan grade
        laptop = assessment.laptop
        laptop.physical_grade = final_grade
        laptop.status = 'assessed'
        laptop.save()
    
    return assessment


def get_grade_recommendation(grade):
    """
    Dapatkan rekomendasi berdasarkan grade
    """
    recommendations = {
        'A': {
            'status': 'Mint/Near Mint',
            'action': 'Siap untuk lelang dengan harga premium',
            'description': 'Tidak ada cacat kosmetik terlihat, fungsi 100% normal, layar bersih tanpa deadpixel.'
        },
        'B': {
            'status': 'Good/Standard',
            'action': 'Siap untuk lelang dengan harga standar',
            'description': 'Cacat kosmetik ringan (goresan halus, dent kecil), layar boleh ada whitespot samar, fungsi normal.'
        },
        'C': {
            'status': 'Fair/Minor Defect',
            'action': 'Perlu perbaikan ringan sebelum lelang',
            'description': 'Cacat kosmetik jelas/berat (deep scratch, retak halus), layar ada deadpixel/bruise, fungsionalitas utuh tapi fisik kurang baik.'
        },
        'D': {
            'status': 'Broken/Salvage',
            'action': 'Dijual sebagai bahan kanibal (parts only)',
            'description': 'Rusak fisik parah, mati total, atau biaya perbaikan melebihi nilai jual.'
        },
    }
    
    return recommendations.get(grade, recommendations['D'])
