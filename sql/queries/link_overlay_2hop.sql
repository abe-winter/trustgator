-- :name link_overlay_2hop :many
with direct_vouchees as (
  select A.userid from assertions A
    join vouches V using (assertid)
    where V.userid = :userid
    and A.userid != :userid
),
indirect_vouchees as (
  select A.userid, avg(score) as avg_score from assertions A
    join vouches V using (assertid)
    where V.userid in (select * from direct_vouchees)
    and A.userid != :userid
    -- keep this commented: we *want* trust info from 2-hop net on direct_vouchees
    -- and A.userid not in (select * from direct_vouchees)
    group by A.userid
)
select A.*, U.username, avg_score from assertions A
  join users U using (userid)
  join indirect_vouchees V using (userid)
  order by A.created;
