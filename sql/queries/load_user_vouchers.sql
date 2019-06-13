-- :name load_user_vouchers :many
with vouchers as (
  select distinct V.userid from vouches V
    join assertions A using (assertid)
    where A.userid = :userid
    and V.userid != :userid
)
select userid, username from users
  where userid in (select * from vouchers)
  limit :limit;
