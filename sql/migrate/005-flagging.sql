create table if not exists link_flags (
  linkid uuid not null,
  userid uuid not null,
  primary key (linkid, userid),
  category text not null, -- 'law' or 'policy'
  detail text not null,
  created timestamp not null default now()
);

create table if not exists assert_flags (
  assertid uuid not null,
  userid uuid not null,
  primary key (assertid, userid),
  category text not null, -- 'law' or 'policy'
  detail text not null,
  created timestamp not null default now()
);
