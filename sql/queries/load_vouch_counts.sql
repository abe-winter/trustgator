-- :name load_vouch_counts
select assertid, score, count(*) from vouches where assertid=any(:assertids) group by assertid, score;
