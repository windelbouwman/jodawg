Development Ideas
=================
(Keep this up to date with anthing that comes to mind)

Stage 1:
* Develop Basic 1-to-1 messenging functionality
  that uses public key encryption.

Thoughts:
1) We want our approach to be as distributed as possible.
   Hence, no centralized 'servers' will be used, though we may
   use stable peers in the network (those exhibiting minimal churn)
   for store-and-forward purposes and for bootstrapping [AT].
2) As I see it there are really two things that can happen when a
   message needs to be delivered to a recipient. When that recipient
   is on-line (and reachable) the message can be delivered DIRECTLY.
   If not, we need to store and forward the message [AT].
3) Windel pointed out that essentially we can view this as a log
   synchronization task. The messages could be seen as "diffs" to a 
   log-file that needs to sync between two (or in the future more) people [AT].
4) Public key infra-structure is an important part of the architecture,
   messenging needs to be secure. Elliptic Curve Cryptography may be the
   a good option, since it uses short public and private keys [AT].
5) Multi-machine operation needs to be supported. This means that a user
   may be logged in using a computer, a mobile phone, a tablet, etc.
   Messages must be properly delivered to all those endpoints, and naturally
   one needs to be able to send them from all those endpoints too.
   This may call for a two-level infra-structure. One that allows secure
   messenging between machines and another that allows one to login to
   the network and allows for messenging between users. The lower level
   could be viewed as a type of basic secure communications infra-structure.
   (which would also enable many other interesting applications in the future) [AT].
6) Initially we should use something simple for communication between peers.
   To keep development time at a minimum, we will use XMLRPC at first [AT].
7) Inspiration may be drawn from XMPP and SIMPLE, the two widely used and
   accepted messenging protocols (Google Talk also uses XMPP, and WhatsApp is
   based on it as well). Though, those protocols are essentially centralized,
   and not truly peer-to-peer [AT].
8) Identifiers on the network should probably be numbers. Profile data can
   be associated with those numbers (nickname, fullname, etc.). Associating
   a (randomly chosen) account number with a VCARD and a public key seems the
   most simple solution [AT].
9) QT can be used to develop the interface, as it easily transfers to multiple platforms as Windel suggested [AT].

Future:
Though we don't want to bloat our protocol in the beginning. I do suggest that we allow for sending audio and video as well eventually. This may influence some design choices in the beginning [AT].

Thoughts on a secure protocol
=============================
Encryption really is only one part of security. There are several others that are important
for a truly reliable secure messaging mechanism. Here are some considerations pulled from other
sources:
1) Perfect-forward secrecy: if a private key is obtained (by a third malicious party) sometime
   in the future, one should not be able to decrypt all the messages sent using that key. A solution
   to this is to use 'session keys', meaning: generating new keys for each session. We can do this
   using node public/private keypairs which cycle regularly. Effectively we are applying two layers
   of encryption. Even if one captures all communication between two nodes, it's impossible to actually
   decrypt that (even if a user's private key is stolen later).
2) Identity Verification: a difficult problem, there is the WOT (web of trust) model employed by PGP,
   unfortunately it is rather cumbersome to confront users with it. Instead a TOFU (trust on first use)
   model is often employed (indeed, BitTorrent also more or less does this with file exchange, combined
   with tit-for-tat).
3) Identity Representation: Many p2p systems use key fingerprint for this, which collapse key and
   identifier into one representation. Problem is that it is not user friendly, so QR codes,
   barcodes and whatnot must be used instead, which may be to cumbersome as well (if they are the
   only option). For now I've chosen a simple numeric identifier. This enabled anonymity more effectively
   than the standard "user@domain.tld" notation. Though, for ease of use one could associate such 
   'profile' fields with an identifier.

See, https://leap.se/en/docs/tech/hard-problems for an overview of big seven problems, copied here:
1) Authenticity problem: Public key validation is very difficult for users to manage, but without it you cannot have confidentiality.
2) Meta-data problem: Existing protocols are vulnerable to meta-data analysis, even though meta-data is often much more sensitive than content.
3) Asynchronous problem: For encrypted communication, you must currently choose between forward secrecy or the ability to communicate asynchronously.
4) Group problem: In practice, people work in groups, but public key cryptography doesn’t.
5) Resource problem: There are no open protocols to allow users to securely share a resource.
6) Availability problem: People want to smoothly switch devices, and restore their data if they lose a device, but this very difficult to do securely.
7) Update problem: Almost universally, software updates are done in ways that invite attacks and device compromises.

How do we handle these problems?
1) I am thinking of a form of hierarchical keysigning (using a limited number of invites).
2) We simply encrypt everything that goes over the wire using session keys (meta-data included).
   That doesn't solve the problem completely though, as we still need a way to be able to 'deny' that
   communication was specifically between two peers. There are some solutions to this, like onion routing.
   I am thinking of scattering copies of messages over the network, where each node tries to decrypt what
   was sent with it's private key. Most will get jibberish, but the target node will be able to succesfully
   decrypt. Perhaps for more deniability, messages must note be signed when communicating at the node level.
3) OTR (off the record) works within a single session by cycling keys for each new session w/o exchange.
   However, there is not asynchronous equivalent for non-live chat. key cycling for node-to-node communication 
   partially solves this. It preserves forward secrecy using the node keys and asynchronous communication
4) One way to solve this is to create group-level keys, but these need to be kept somewhere. Hence, we
   are essentially stuck with re-encrypting messages to each client. It think that's okay for now, but
   it does not scale up very well of course.
5) This can be solved by putting ALL data in band (not linking to external, unsecure sources). This is okay
   for images and such, but for URL's for example it's impossible ...
6) Nodes should synchronize their (user) data as well.
7) We should think hard about how updates should be rolled out, to prevent creating a major loophole there ...

Some more on OTR: https://whispersystems.org/blog/simplifying-otr-deniability/