-- person
--     person_id, 
--     first_name, 
--     last_name

-- address
--     address_id, 
--     person_id, 
--     city, 
--     state


-- Return `first_name, last_name, city, state` for every person. People with no
-- address on file should still appear, with `city`/`state` as `NULL`.


select
    person.first_name,
    person.last_name,
    address.city,
    address.state
from person
left join adress on adress.person_id = person.person_id;


