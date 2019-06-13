-- :name get_user_asserts :many
select L.linkid, assertid, title, topic, claim, A.created from assertions A
  join links L using (linkid)
  where A.userid = :userid
  order by A.created desc
  limit :limit;
