-- :name load_global_active :many
with assert_counts as (
  select linkid, count(*) as assert_count,
    extract(epoch from age(links.created)) / 3600 as hours_old
    from links
    left join assertions using (linkid)
    where links.created > (select min(created) from (select created from links order by created desc limit :wide_count) as sub1)
    group by linkid
),
ranked as (
  select linkid, assert_count,
    assert_count / (case when hours_old > 6 then hours_old else 6 end) as score
    from assert_counts
    order by score desc
    limit :narrow_count
)
select L.*, assert_count, U.username, score from ranked
  join links L using (linkid)
  join users U using (userid)
  order by score desc;
