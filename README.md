# trustgator

![trustgator the trustgator gator fetching a newspaper as a dog might](./logo/gator.png)

Trustgator is a link aggregator (i.e. reddit clone) with a two-hop trust network built in.

There's a demo of this up at [trustgator.page](https://trustgator.page).

The overall goal here is to understand how the people in your network view a particular piece of information, and to weight that by topic expertise.

## Trust features

### Assertions

Users can 'assert' claims about articles which are visible in the article's thread. Assertions have an attached topic so you may end up trusting a certain user on 'long haul trucking' but not on 'modern dance'.

### Vouches

Users can 'vouch' for assertions that interest them. Vouches can be positive but also neutral i.e. 'interesting but not sure' or negative i.e. 'disagree'. The goal isn't to hide content you disagree with.

### Surfaced articles

* The articles on a user's homepage are those with recent assert/vouch activity from their 2-hop network (i.e. users you've vouched and users your vouchees have vouched)
* todo: also articles that are active in the overall community / your topic mix

### RFCs

(🚧🚧🚧 todo) Users can 'ping' their trust network with a request for comment. This alerts the network to look at an article and comment on it.

## Running your own

* I use the helm chart (under deploy/trustgator) to run the demo site on kube
* check deploy/README.md for more info

## FAQs

### Isn't this just twitter?

Differences:

* this uses 2-hop trust to show you content (twitter is 1-hop follow, although the retweet model acts sometimes like a two-hop system)
* the primary content is external links rather than user-authored tweets
* negative vouches -- unlike twitter, our network includes disagreement
* tagged expertise -- a single user account has different network trust scores for different topics
* no 'reply' semantic -- TG users aren't directly responding to each other

### Why does 2nd-degree trust matter?

* It gives you access to information from useful strangers who are trusted by your group
* Bad 2-hop information can affect how you trust your 1-hop group; if you tend to give negative vouches to users downstream of a user you follow directly, that can weight down the score of the direct-followed user
* Most systems have these concepts built in as recommmendation systems; amazon has been doing it since the 90s with collaborative filtering, which tries to fit you into. TG is designed to make multihop connections explicit and useful to the user.

The trust network features are a work in progress.

## Todo

### Write tests for

* the queries in trustgraph.py
* the helper functions / classes in util (Degraded class, cache_wrapper decorator)
* signup logic (esp invite code state space)
* is_invitee
