INSERT INTO transaksi_pembelian 
(id_pelanggan, id_kendaraan, tanggal_transaksi, tanggal_pembelian, jumlah, harga_beli)
VALUES (
    (SELECT id FROM pelanggan WHERE nama = 'Andi Wijaya'),
    (SELECT id FROM kendaraan WHERE model = 'Triton'),
    NULL,  -- Diberikan NULL secara eksplisit untuk menguji
    '2025-03-12',
    1,
    (SELECT harga FROM kendaraan WHERE model = 'Triton')
);
