-- :name load_assert_vouches :many
select vouches.*, users.username from vouches
  join users using (userid)
  where assertid = :assertid;
