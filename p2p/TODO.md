Almer's TODO's:
*) Get the OverlayService running with multiple nodes and proper join/leave
   functionality. This is fairly simple:
   1) Hardcode a bootstrap peer (and run an instance on that particular ip/port, different account perhaps)
   2) Start a second peer that connects to the bootstrap peer.
   3) Have the peers exchange their "known peers" OverlayStore (and redesign that to only hold nodes, not users).
   4) Make sure that a node executed a "node_leave" to the network when terminate() is invoked (and the node is joined to the network).
   5) Allow "leave" from the shell to execute command_leave() as well.
   6) Perhaps create a small test script that does this automatically with an N number of peers.
*) Design the user login (&logout) negotiation.
   This will take a bit more work. Difficulty is that this 'ties in' with adding users to the network. For now we can handle manually
   maintaining a user database (perhaps as part of the overlay store, though I'd like to have that separate).

Future Work:
*) A node's key never expires right now, this needs to be changed, so that a node cycles it's keypair every N hours or so.
   Problem is that this will make bootstrapping more difficult (as this requires a list with (node_address, node_public_key) pairs,
   which will become defunct if a node key-cycles). Hence, the 'expiry' should somehow depend on the network size. We can assume a long
   limit for the time being, but this needs to be investigated more thoroughly.
*) I suggest a third encryption layer for exchanging messages, either real-time or not. This adds some complexity to the algorithm, but
   it also enabled perfect forward secrecy :D
x
