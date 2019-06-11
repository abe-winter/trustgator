-- :name insert_link :1
insert into links (userid, title, url) values (:userid, :title, :url) returning linkid;
