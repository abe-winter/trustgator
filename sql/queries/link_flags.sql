-- :name link_flags :many
select link_flags.*, users.username from link_flags
  join users using (userid)
  where linkid = :linkid
  order by created;
