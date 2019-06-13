-- :name load_join_assert :1
select A.*, L.linkid, L.title, U.username from assertions A
  join links L using (linkid)
  join users U on A.userid = U.userid
  where assertid = :assertid;
