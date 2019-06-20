-- :name load_link :1
select links.*, username from links
  join users using (userid)
  where linkid = :linkid;
