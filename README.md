# forum-over-stem

## Summary

* Use stem, which is a python wrapper of Tor, to communicate anonymously.

* The server could handle HTTP GET/POST request and websocket request.

* Notice that the client could sign and POST binary data to the server and the server could verify it. 

* mycurl.sh: a curl client for testing.

* The additional packages are listed in requirements.txt


## to-do-list
* I haven't tested whether the server could get the client address;

* The basic architecture of this forum is based on P2P network. For simplicity, I started with the structure of Server/Client.

* Add code to support SSL communication.
