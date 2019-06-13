-- :name links_2hop :many
with direct_vouchees as (
  select A.userid from assertions A
    join vouches V using (assertid)
    where V.userid = :userid
    and A.userid != :userid
),
indirect_vouchees as (
  select A.userid from assertions A
    join vouches V using (assertid)
    where V.userid in (select * from direct_vouchees)
    and A.userid != :userid
    and A.userid not in (select * from direct_vouchees)
),
recent_asserted as (
  select L.linkid from links L
    join assertions A using (linkid)
    where A.userid in (select * from indirect_vouchees)
    order by A.created desc
    limit :limit
)
select L.*, U.username from links L
  join users U on L.userid = U.userid
  where linkid in (select * from recent_asserted)
  or L.userid in (select * from indirect_vouchees)
  order by L.created desc
  limit :limit;
