-- :name insert_assert :1
insert into assertions (userid, linkid, topic, claim) values (:userid, :linkid, :topic, :claim) returning assertid;
