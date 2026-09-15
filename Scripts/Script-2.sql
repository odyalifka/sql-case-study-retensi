-- sama dengan

select 1 = 1;
select 1 = 2;

select *
from actor a 
where first_name = 'John'

-- tidak sama dengan
select 1 != 1;
select 1 != 2;
select 1 <> 1;

select *
from address a 
where district != 'Texas'

-- lebih besar 

select title , length 
from film f 
where length > 60;

-- lebih besar dari atau sama dengan

select title , length
from film f 
where length >= 60

-- lebih kecil

select title , length 
from film f 
where length < 60;

-- lebih kecil dari atau sama dengan

select title , length 
from film f 
where length <= 60;