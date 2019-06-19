-- :name flag_link
insert into link_flags (linkid, userid, category, detail)
  values (:linkid, :userid, :category, :detail);
