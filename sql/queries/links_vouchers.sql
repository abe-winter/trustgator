-- :name links_vouchers :many
with vouchers as (
  select V.userid from assertions A
    join vouches V using (assertid)
    where A.userid = :userid
    and V.userid != :userid
),
recent_asserted as (
  select L.linkid from links L
    join assertions A using (linkid)
    where A.userid in (select * from vouchers)
    order by A.created desc
    limit :limit
)
select L.*, U.username from links L
  join users U on L.userid = U.userid
  where linkid in (select * from recent_asserted)
  or L.userid in (select * from vouchers)
  order by L.created desc
  limit :limit;
