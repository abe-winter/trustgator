# trustgator

![trustgator the trustgator gator fetching a newspaper as a dog might](./logo/gator.png)

Trustgator is a link aggregator (i.e. reddit clone) with a two-hop trust network built in.

There's a demo of this up at [trustgator.page](https://trustgator.page).

The overall goal here is to understand how the people in your network view a particular piece of information, and to weight that by topic expertise.

Nothing fancy here is happening on the technology side -- the goal is to let users understand information in the context of people whose opinions they like.

## Trust features

### Assertions

Users can 'assert' claims about articles which are visible in the article's thread. Assertions have an attached topic so you may end up trusting a certain user on 'long haul trucking' but not on 'modern dance'.

### Vouches

Users can 'vouch' for assertions that interest them. Vouches can be positive but also neutral i.e. 'interesting but not sure' or negative i.e. 'disagree'. The goal isn't to hide content you disagree with.

### 'Top articles'

* The articles on a user's homepage are those with recent assert/vouch activity from their 2-hop network (i.e. users you've vouched and users your vouchees have vouched)
* todo: also articles that are active in the overall community / your topic mix

### RFCs

Users can 'ping' their trust network with a request for comment. This alerts the network to look at an article and comment on it.
