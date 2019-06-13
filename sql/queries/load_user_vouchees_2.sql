-- :name load_user_vouchees_2 :many
with direct_vouchees as (
  select distinct A.userid from assertions A
    join vouches V using (assertid)
    where V.userid = :userid
),
indirect_vouchees as (
  select distinct A.userid from assertions A
    join vouches V using (assertid)
    where V.userid in (select * from direct_vouchees)
    and A.userid not in (select * from direct_vouchees)
    and A.userid != :userid
)
select userid, username from users
  where userid in (select * from indirect_vouchees)
  limit :limit;
