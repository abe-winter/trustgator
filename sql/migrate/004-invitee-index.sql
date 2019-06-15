create index if not exists invitations_redeemer on invitations (redeemed_userid) where redeemed_userid is not null;
