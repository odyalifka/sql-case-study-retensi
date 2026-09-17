from sqlalchemy import create_engine
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt

engine = create_engine('postgresql://postgres@localhost:5432/olist_ecommerce')

# ==== STEP 1: Ambil fitur dari transaksi pertama setiap pelanggan ====
query_fitur = """
WITH first_order AS (
  SELECT
    c.customer_unique_id,
    o.order_id,
    o.order_purchase_timestamp::timestamp AS purchase_date,
    ROW_NUMBER() OVER (
      PARTITION BY c.customer_unique_id 
      ORDER BY o.order_purchase_timestamp::timestamp
    ) AS rn
  FROM olist_orders_dataset o
  JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
)
SELECT
    fo.customer_unique_id,
    fo.order_id,
    oi.price,
    oi.freight_value,
    pt.product_category_name_english AS kategori_produk,
    op.payment_type,
    op.payment_installments,
    r.review_score,
    EXTRACT(EPOCH FROM (
      o.order_delivered_customer_date::timestamp - o.order_purchase_timestamp::timestamp
    )) / 86400 AS lama_pengiriman_hari,
    c.customer_state
FROM first_order fo
JOIN olist_orders_dataset o ON fo.order_id = o.order_id
JOIN olist_customers_dataset c ON fo.customer_unique_id = c.customer_unique_id AND o.customer_id = c.customer_id
JOIN olist_order_items_dataset oi ON fo.order_id = oi.order_id
LEFT JOIN olist_products_dataset p ON oi.product_id = p.product_id
LEFT JOIN product_category_name_translation pt ON p.product_category_name = pt.product_category_name
LEFT JOIN olist_order_payments_dataset op ON fo.order_id = op.order_id
LEFT JOIN olist_order_reviews_dataset r ON fo.order_id = r.order_id
WHERE fo.rn = 1
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_delivered_customer_date != ''
"""
print("Mengambil data fitur dari database...")
df_fitur = pd.read_sql(query_fitur, engine)
print(f"Jumlah baris fitur: {len(df_fitur)}")

# ==== STEP 2: Ambil label (siapa yang balik lagi, dari logika case study 1) ====
query_label = """
SELECT DISTINCT
    c.customer_unique_id,
    DATE(o.order_purchase_timestamp::timestamp) AS tanggal_kunjungan
FROM olist_orders_dataset o
JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
WHERE o.order_status != 'canceled'
"""
print("Mengambil data kunjungan untuk membuat label...")
df_kunjungan = pd.read_sql(query_label, engine)
df_kunjungan = df_kunjungan.sort_values(['customer_unique_id', 'tanggal_kunjungan'])
df_kunjungan['urutan'] = df_kunjungan.groupby('customer_unique_id').cumcount() + 1

jumlah_kunjungan = df_kunjungan.groupby('customer_unique_id')['urutan'].max().reset_index()
jumlah_kunjungan['is_repeat'] = (jumlah_kunjungan['urutan'] >= 2).astype(int)

# ==== STEP 3: Gabungkan fitur dan label ====
df = df_fitur.merge(
    jumlah_kunjungan[['customer_unique_id', 'is_repeat']], 
    on='customer_unique_id', how='inner'
)
# Hapus duplikat pelanggan (kalau ada, jaga-jaga dari JOIN yang menghasilkan baris ganda)
df = df.drop_duplicates(subset='customer_unique_id')
print(f"Jumlah pelanggan setelah digabung: {len(df)}")
print(f"Distribusi label:\n{df['is_repeat'].value_counts()}")

# ==== STEP 4: Bersihkan data ====
df = df.dropna(subset=['price', 'freight_value', 'lama_pengiriman_hari', 'review_score'])
df['kategori_produk'] = df['kategori_produk'].fillna('unknown')
df['payment_type'] = df['payment_type'].fillna('unknown')
df['payment_installments'] = df['payment_installments'].fillna(1)

# Gabungkan kategori produk yang jarang muncul (<200 transaksi) jadi satu grup "other"
jumlah_per_kategori = df['kategori_produk'].value_counts()
kategori_jarang = jumlah_per_kategori[jumlah_per_kategori < 200].index
df['kategori_produk'] = df['kategori_produk'].apply(
    lambda x: 'other' if x in kategori_jarang else x
)
print(f"\nJumlah kategori produk setelah digabung: {df['kategori_produk'].nunique()}")

# ==== STEP 5: Siapkan data untuk model ====
df_model = pd.get_dummies(
    df[['price', 'freight_value', 'payment_installments', 'review_score', 
        'lama_pengiriman_hari', 'kategori_produk', 'payment_type', 'is_repeat']],
    columns=['kategori_produk', 'payment_type'],
    drop_first=True
)

X = df_model.drop('is_repeat', axis=1)
y = df_model['is_repeat']

# ==== STEP 6: Split data latih dan data uji ====
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==== STEP 7: Latih model ====
model = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
model.fit(X_train_scaled, y_train)

# ==== STEP 8: Evaluasi ====
y_pred = model.predict(X_test_scaled)
print("\n=== HASIL EVALUASI MODEL (setelah perbaikan) ===")
print(classification_report(y_test, y_pred, target_names=['Tidak balik', 'Balik lagi']))

cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(cm)

# ==== STEP 9: Fitur paling berpengaruh ====
koefisien = pd.DataFrame({
    'fitur': X.columns,
    'pengaruh': model.coef_[0]
}).sort_values('pengaruh', key=abs, ascending=False)

print("\n=== 15 FITUR PALING BERPENGARUH ===")
print(koefisien.head(15).to_string(index=False))


from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve

# ==== PERCOBAAN TAMBAHAN: Random Forest ====
rf_model = RandomForestClassifier(
    n_estimators=300, max_depth=6, class_weight='balanced', 
    random_state=42, n_jobs=-1
)
rf_model.fit(X_train, y_train)  # Random Forest tidak butuh data yang di-scale

y_proba_rf = rf_model.predict_proba(X_test)[:, 1]
y_proba_lr = model.predict_proba(X_test_scaled)[:, 1]

print("\n=== PERBANDINGAN KUALITAS MODEL (ROC-AUC & PR-AUC) ===")
print(f"Logistic Regression - ROC-AUC: {roc_auc_score(y_test, y_proba_lr):.3f} | PR-AUC: {average_precision_score(y_test, y_proba_lr):.3f}")
print(f"Random Forest        - ROC-AUC: {roc_auc_score(y_test, y_proba_rf):.3f} | PR-AUC: {average_precision_score(y_test, y_proba_rf):.3f}")
print(f"(Sebagai pembanding, kalau model asal tebak: PR-AUC seharusnya sekitar {y_test.mean():.3f}, sesuai proporsi kelas 'Balik lagi')")

# Fitur penting menurut Random Forest
feat_importance = pd.DataFrame({
    'fitur': X.columns,
    'kepentingan': rf_model.feature_importances_
}).sort_values('kepentingan', ascending=False)

print("\n=== 10 FITUR TERPENTING MENURUT RANDOM FOREST ===")
print(feat_importance.head(10).to_string(index=False))

# ==== CHART: Precision-Recall Curve (model vs baseline) ====
from sklearn.metrics import precision_recall_curve

precision_lr, recall_lr, _ = precision_recall_curve(y_test, y_proba_lr)
precision_rf, recall_rf, _ = precision_recall_curve(y_test, y_proba_rf)
baseline = y_test.mean()

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(recall_lr, precision_lr, label=f'Logistic Regression (AUC={average_precision_score(y_test, y_proba_lr):.3f})', color='#2563eb')
ax.plot(recall_rf, precision_rf, label=f'Random Forest (AUC={average_precision_score(y_test, y_proba_rf):.3f})', color='#16a34a')
ax.axhline(y=baseline, color='#dc2626', linestyle='--', label=f'Random guess baseline ({baseline:.3f})')
ax.set_xlabel('Recall')
ax.set_ylabel('Precision')
ax.set_title('Precision-Recall Curve: Model vs Random Guess Baseline')
ax.legend()
plt.tight_layout()
plt.savefig('chart_pr_auc.png', dpi=150)
plt.show()

# ==== CHART: Feature importance (Random Forest) ====
top10_rf = feat_importance.head(10).sort_values('kepentingan')
fig2, ax2 = plt.subplots(figsize=(8, 6))
ax2.barh(top10_rf['fitur'], top10_rf['kepentingan'], color='#2563eb')
ax2.set_title('Top 10 Feature Importance (Random Forest)')
ax2.set_xlabel('Importance')
plt.tight_layout()
plt.savefig('chart_feature_importance_rf.png', dpi=150)
plt.show()