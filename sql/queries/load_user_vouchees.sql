-- :name load_user_vouchees :many
with vouchees as (
  select distinct A.userid from assertions A
    join vouches V using (assertid)
    where V.userid = :userid
    and A.userid != :userid
)
select userid, username from users
  where userid in (select * from vouchees)
  limit :limit;
