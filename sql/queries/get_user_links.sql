-- :name get_user_links :many
select * from links where userid = :userid
  order by created desc
  limit :limit;
