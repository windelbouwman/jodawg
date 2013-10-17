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

