# Script to fix laptop_list.html template
import pathlib

content = '''{% extends 'base.html' %}

{% block title %}Master Data Aset{% endblock %}

{% block content %}
<div class="page-header d-flex justify-content-between align-items-start">
    <div>
        <h2>Halaman Daftar Seluruh Aset</h2>
        <p>Kelola dan pantau seluruh aset IT perusahaan</p>
    </div>
    <a href="{% url 'inventory:laptop_create' %}" class="btn btn-add">
        <i class="bi bi-plus-lg"></i> Tambah Aset Baru
    </a>
</div>

<div class="data-table mb-4">
    <div class="p-3">
        <form method="get" class="row g-3 align-items-end">
            <div class="col-md-4">
                <input type="text" name="q" class="form-control" placeholder="Cari aset..." value="{{ search_query }}">
            </div>
            <div class="col-md-2">
                <button type="submit" class="btn btn-outline-secondary w-100">Filter</button>
            </div>
        </form>
    </div>
</div>

<div class="data-table">
    <table class="table table-hover mb-0">
        <thead>
            <tr>
                <th>No</th>
                <th>Kode Aset</th>
                <th>Nomor Serial</th>
                <th>Merk</th>
                <th>Model</th>
                <th>User Terakhir</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {% for laptop in laptops %}
            <tr>
                <td>{{ forloop.counter }}</td>
                <td><a href="{% url 'inventory:laptop_detail' laptop.pk %}">{{ laptop.asset_code }}</a></td>
                <td>{{ laptop.serial_number }}</td>
                <td>{{ laptop.brand }}</td>
                <td>{{ laptop.model }}</td>
                <td>{{ laptop.last_user }}</td>
                <td>
                    {% if laptop.status == 'assessed' %}
                    <span class="badge-status badge-ready">Sudah Dinilai</span>
                    {% else %}
                    <span class="badge-status badge-draft">{{ laptop.get_status_display }}</span>
                    {% endif %}
                </td>
            </tr>
            {% empty %}
            <tr><td colspan="7" class="text-center py-4">Belum ada data</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}'''

path = pathlib.Path(r'd:\Coba\KKL\inventory\templates\inventory\laptop_list.html')
path.write_text(content, encoding='utf-8')
print('Template fixed successfully!')
