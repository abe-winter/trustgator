create table if not exists invitations (
  inviteid uuid primary key default uuid_generate_v4(),
  userid uuid not null, -- this is the issuing user
  code text not null unique,
  redeemed_userid uuid,
  created timestamp not null default now(),
  redeemed timestamp
);
