-- initial.sql

create extension if not exists "uuid-ossp";

create table if not exists users (
  userid uuid primary key default uuid_generate_v4(),
  username text not null unique,
  password bytea,
  created timestamp not null default now(),
  modified timestamp not null default now(),
  delete_on timestamp -- account deletion is undoable for N days
);

create table if not exists links (
  linkid uuid primary key default uuid_generate_v4(),
  userid uuid not null,
  url text,
  created timestamp not null default now()
);

create index if not exists links_userid on links (userid);

create table if not exists assertions (
  assertid uuid primary key default uuid_generate_v4(),
  userid uuid not null,
  linkid uuid not null,
  topic text,
  claim text,
  created timestamp not null default now()
);

create index if not exists assert_userid on assertions (userid);
create index if not exists assert_linkid on assertions (linkid);

create table if not exists vouches (
  userid uuid not null,
  assertid uuid not null,
  primary key (userid, assertid),
  score smallint not null,
  created timestamp not null default now()
);

create table if not exists rfcs (
  rfcid uuid primary key default uuid_generate_v4(),
  userid uuid not null,
  linkid uuid not null,
  content text,
  created timestamp not null default now()
);

create index if not exists rfc_userid on rfcs (userid);
create index if not exists rfc_linkid on rfcs (linkid);
