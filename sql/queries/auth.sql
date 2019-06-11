-- :name insert_user :1
insert into users (username, password, email) values (:username, :password, :email) returning userid;
