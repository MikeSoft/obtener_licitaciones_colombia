select titulo,link from licitaciones where titulo in (select titulo from licitaciones group by titulo having count(*) >1)
select titulo from licitaciones group by titulo having count(*) >1
select * from licitaciones where titulo = "Proceso 66-195-2017"