-- :name insert_invite :1
insert into invitations (userid, code) values (:userid, :code) returning inviteid;
