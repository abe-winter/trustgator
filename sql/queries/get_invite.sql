-- :name get_invite :1
select * from invitations where code = :code;
