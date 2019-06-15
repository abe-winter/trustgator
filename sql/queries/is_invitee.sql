-- :name is_invitee :1
select count(*) from invitations where redeemed_userid = :userid;
