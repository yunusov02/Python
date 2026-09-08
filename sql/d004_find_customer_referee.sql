-- Customer(id, name, referee_id)

select
    c.id,
    c.name
from customer c
where referee_id <> 2 or referee_id is null

