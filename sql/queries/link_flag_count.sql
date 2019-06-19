-- :name link_flag_count :1
select count(*) from link_flags where linkid = :linkid;
