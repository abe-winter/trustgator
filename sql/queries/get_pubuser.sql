-- :name get_pubuser :1
select userid, username, delete_on from users where userid = :userid;
