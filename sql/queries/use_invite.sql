-- :name use_invite
update invitations
  set redeemed_userid = :userid, redeemed = now()
  where code = :code and redeemed_userid is null and redeemed is null;
