select *
from actor;

select first_name , last_name
from actor a ;

select *
from actor a
where first_name = 'John'

select *
from film

select *
from film
where rental_duration = '3' 

select title, release_year, rating
from film
limit 10

select title, release_year, rating
from film
order by title desc
limit 10

select title, release_year, rating
from film
limit 5
offset 8

select
title "Judul Film"
release_year "Harga Sewa"
from film;