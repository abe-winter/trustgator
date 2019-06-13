-- :name links_1hop :many
with vouchees as (
  select A.userid from assertions A
    join vouches V using (assertid)
    where V.userid = :userid
    and A.userid != :userid
),
recent_asserted as (
  select L.linkid from links L
    join assertions A using (linkid)
    where A.userid in (select * from vouchees)
    order by A.created desc
    limit :limit
)
select L.*, U.username from links L
  join users U on L.userid = U.userid
  where linkid in (select * from recent_asserted)
  or L.userid in (select * from vouchees)
  order by L.created desc
  limit :limit;
-- todo: include articles posted by people whose posts you've asserted? meh
-- todo: this won't scale well as the DB grows
