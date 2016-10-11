This sandbox folder contains some test code for the Tornado web framework.

* `server.py` Defines a web app that simulates concurrent computations both by means of a RESTful API and a WebSocket. 
* `client.py` Sends non-blocking computation requests to the server and receives results asynchronously.
    
Run server first, then the client. Observe how requests are executed concurrently by watching the console outputs of server and client.

