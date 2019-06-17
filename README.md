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

* this uses 2-hop trust to show you content (twitter is 1-hop follow, although the retweet model and suggested accoutns are sometimes like a two-hop system)
* the primary content is external links rather than user-authored tweets
* negative vouches -- unlike twitter, our network includes disagreement
* tagged expertise -- a single user account has different network trust scores for different topics

### What is the 2-hop trust model?

Every product that makes suggestions to you has an implicit model of multi-hop trust. For example:

* twitter suggests who to follow based on who you follow
* G rewrites your search terms based on other people's behavior
* amzn 'collaborative filtering' is the oldest trick in the book -- suggest more purchases based on your browse purchase behavior

**All of these are implicit**. Trustgator is **explicit** in that it:

* Doesn't extend beyond the second hop, i.e. 'friends of friends'. ML-based products will typically train on the entire community.
* Distinguishes 1-hop content from 2-hop content, i.e. distinguishes people you acted to include vs people you reached through the network.

All 'suggestion' products are making a compromise between 'discovery' (access to interesting or useful things) and 'trust' (fairness / accuracy of a news article, validity of an opinion, honesty of a review).

Trustgator is an experiment to make that compromise more transparent by overlaying your trust network on the UX and explaining the origin of suggestions.

My thesis is that people are dumb at evaluating the validity of blind recommendations but smart at understanding when questionable content all comes via a certain person.

## Todo

### Write tests for

* the queries in trustgraph.py
* the helper functions / classes in util (Degraded class, cache_wrapper decorator)
* signup logic (esp invite code state space)
