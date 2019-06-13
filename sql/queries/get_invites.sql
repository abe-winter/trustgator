-- :name get_invites :many
select I.*, U.username from invitations I
  left join users U on I.redeemed_userid = U.userid
  where I.userid = :userid;
