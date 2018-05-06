# ProtoN Echo Server
The echo server can be tested by the following commands from a \*nix CLI:

```bash
export FLASK_APP=server.py
flask run
```

Proton's functionality can then be tested from the JS console with:

```js
proton.get('http://localhost:5000/echo', {'Hello': 'World'}, console.log);
proton.post('http://localhost:5000/echo', {'Hello World': true}, console.log);
```
