-- :name get_user_vouches :many
select linkid, title, A.assertid, score, topic, claim, U.userid, U.username, V.created from vouches V
  join assertions A using (assertid)
  join links L using (linkid)
  join users U on A.userid = U.userid
  where V.userid = :userid
  order by V.created desc
  limit :limit;
