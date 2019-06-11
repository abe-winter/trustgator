-- :name load_link_asserts :many
select assertions.*, username
  from assertions
  join users using (userid)
  where linkid = :linkid
  order by created;
