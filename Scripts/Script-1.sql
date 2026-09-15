-- menulis ALIAS menggunakan AS
select 
title as judul,
rental_rate as harga_sewa
from film;

-- menulis ALIAS tanpa menggunakan AS
select 
title judul,
rental_rate harga_sewa
from film;

-- menulis judul kolom alias menggunakan spasi
select 
title "Judul Film",
rental_rate "Harga Sewa"
from film;

-- menggunakan ALIAS untuk nama tabel

select 
f.film_id ,
f.title ,
f.release_year ,
f.rental_rate ,
c."name" 
from film f
join film_category fc
on f.film_id = fc.film_id 
join category c
on fc.category_id = c.category_id ;

-- menggunakan ALIAS untuk nama kolom
select 
f.film_id as id_film,
f.title as judul_film,
f.release_year as tahun_perilisan,
f.rental_rate as harga_sewa,
c."name" as kategori_film
from film f
join film_category fc
on f.film_id = fc.film_id 
join category c
on fc.category_id = c.category_id ;

-- menggunakan ALIAS bersama fungsi agregat (SUM, MIN, MAX, AVG, COUNT)
select 
sum(amount) total_pendapatan, 
count(*) jumlah_transaksi, 
min(amount) pembayaran_minimum,
max(amount) pembayaran_maksimum,
avg(amount) pembayaran_ratarata
from payment p 

-- menggunakan ALIAS pada JOINS
select 
f.film_id ,
f.title ,
f.release_year ,
f.rental_rate ,
c."name" 
from film f
join film_category fc
on f.film_id = fc.film_id 
join category c
on fc.category_id = c.category_id ;


-- menggunakan ALIAS pada SUBQUERY

SELECT
	*
from 
(select 
*
from film f
join film_category fc
on f.film_id = fc.film_id 
join category c
on fc.category_id = c.category_id
where f.length >= 60) as film_data_60