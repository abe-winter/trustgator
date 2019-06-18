-- :name link_overlay_1hop :many
with vouchees as (
  select A.userid, avg(score) as avg_score from assertions A
    join vouches V using (assertid)
    where V.userid = :userid
    and A.userid != :userid
    group by A.userid
)
select A.*, U.username, avg_score from assertions A
  join users U using (userid)
  join vouchees V using (userid)
  where linkid = :linkid
  order by A.created;
