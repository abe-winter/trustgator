-- :name ever_vouched :1
select count(*) from vouches
  join assertions A using (assertid)
  where A.userid = :userid;
