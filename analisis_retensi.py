from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt

engine = create_engine('postgresql://postgres@localhost:5432/olist_ecommerce')

# Ambil data mentah: setiap kunjungan (order digabung per hari per pelanggan)
query = """
SELECT DISTINCT
    c.customer_unique_id,
    DATE(o.order_purchase_timestamp::timestamp) AS tanggal_kunjungan
FROM olist_orders_dataset o
JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
WHERE o.order_status != 'canceled'
"""
df = pd.read_sql(query, engine)

# Urutkan kunjungan per pelanggan
df = df.sort_values(['customer_unique_id', 'tanggal_kunjungan'])
df['urutan_kunjungan'] = df.groupby('customer_unique_id').cumcount() + 1

# ==== CHART 1: Retensi pelanggan ====
total_pelanggan = df['customer_unique_id'].nunique()
pelanggan_repeat = df[df['urutan_kunjungan'] >= 2]['customer_unique_id'].nunique()
pelanggan_sekali = total_pelanggan - pelanggan_repeat

fig1, ax1 = plt.subplots(figsize=(6, 5))
ax1.bar(['Beli 1x saja', 'Beli 2x atau lebih'], [pelanggan_sekali, pelanggan_repeat], 
        color=['#cccccc', '#2563eb'])
ax1.set_title('Distribusi Pelanggan: Sekali Beli vs Repeat Order')
ax1.set_ylabel('Jumlah Pelanggan')
for i, v in enumerate([pelanggan_sekali, pelanggan_repeat]):
    ax1.text(i, v + 500, f'{v:,}', ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig('chart_retensi.png', dpi=150)
plt.show()

# ==== CHART 2: Distribusi jeda hari antar kunjungan pertama-kedua ====
kunjungan_12 = df[df['urutan_kunjungan'].isin([1, 2])].pivot(
    index='customer_unique_id', columns='urutan_kunjungan', values='tanggal_kunjungan'
)
kunjungan_12.columns = ['kunjungan_1', 'kunjungan_2']
kunjungan_12 = kunjungan_12.dropna()
kunjungan_12['jeda_hari'] = (
    pd.to_datetime(kunjungan_12['kunjungan_2']) - pd.to_datetime(kunjungan_12['kunjungan_1'])
).dt.days

fig2, ax2 = plt.subplots(figsize=(7, 5))
ax2.hist(kunjungan_12['jeda_hari'], bins=30, color='#2563eb', edgecolor='white')
ax2.axvline(kunjungan_12['jeda_hari'].median(), color='red', linestyle='--', 
            label=f"Median: {kunjungan_12['jeda_hari'].median():.0f} hari")
ax2.set_title('Distribusi Jeda Hari Antara Kunjungan Pertama dan Kedua')
ax2.set_xlabel('Jeda (hari)')
ax2.set_ylabel('Jumlah Pelanggan')
ax2.legend()
plt.tight_layout()
plt.savefig('chart_jeda_hari.png', dpi=150)
plt.show()

print(f"Total pelanggan: {total_pelanggan:,}")
print(f"Pelanggan repeat: {pelanggan_repeat:,}")
print(f"Persentase retensi: {100*pelanggan_repeat/total_pelanggan:.2f}%")
print(f"Median jeda hari: {kunjungan_12['jeda_hari'].median():.0f}")