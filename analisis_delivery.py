from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt

engine = create_engine('postgresql://postgres@localhost:5432/olist_ecommerce')

query = """
SELECT
    o.order_id,
    r.review_score,
    EXTRACT(EPOCH FROM (
        o.order_delivered_customer_date::timestamp - o.order_estimated_delivery_date::timestamp
    )) / 86400 AS selisih_hari
FROM olist_orders_dataset o
JOIN olist_order_reviews_dataset r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
    AND o.order_estimated_delivery_date IS NOT NULL
    AND o.order_delivered_customer_date != ''
    AND o.order_estimated_delivery_date != ''
"""
df = pd.read_sql(query, engine)

# Kategorikan sama seperti di SQL
def kategori(hari):
    if hari <= 0:
        return '1. On-time /\nEarly'
    elif hari <= 3:
        return '2. Late\n1-3 days'
    elif hari <= 7:
        return '3. Late\n4-7 days'
    elif hari <= 14:
        return '4. Late\n8-14 days'
    else:
        return '5. Late\n14+ days'

df['kategori'] = df['selisih_hari'].apply(kategori)

summary = df.groupby('kategori')['review_score'].agg(['mean', 'count']).reset_index()
summary = summary.sort_values('kategori')

# ==== CHART: Rata-rata review score per kategori keterlambatan ====
fig, ax = plt.subplots(figsize=(9, 5.5))
colors = ['#16a34a', '#84cc16', '#f59e0b', '#f97316', '#dc2626']
bars = ax.bar(summary['kategori'], summary['mean'], color=colors)

for bar, mean_val, count_val in zip(bars, summary['mean'], summary['count']):
    ax.text(bar.get_x() + bar.get_width()/2, mean_val + 0.08, 
            f'{mean_val:.2f}\n(n={count_val:,})', 
            ha='center', fontsize=9, fontweight='bold')

ax.set_title('Average Review Score by Delivery Delay', fontsize=13, fontweight='bold')
ax.set_ylabel('Average Review Score (1-5)')
ax.set_ylim(0, 5.5)
ax.axhline(y=summary['mean'].iloc[0], color='gray', linestyle=':', alpha=0.5)
plt.tight_layout()
plt.savefig('chart_delivery_rating.png', dpi=150)
plt.show()

print(summary.to_string(index=False))