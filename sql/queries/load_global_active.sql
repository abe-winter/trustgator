-- :name load_global_active :many
with assert_counts as (
  select linkid, count(*) as assert_count from links
    join assertions using (linkid)
    where links.created > (select min(created) from (select created from links order by created desc limit :wide_count) as sub1)
    group by linkid
    order by assert_count desc
    limit :narrow_count
)
select L.*, assert_count, U.username from assert_counts
  join links L using (linkid)
  join users U using (userid)
  order by assert_count desc;
