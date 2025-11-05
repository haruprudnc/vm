## 「POST /submit-info」
### client -> tracker
```json
{
    "peer_id": "peer_id",
    "ip": "ip",
    "port": "port",
    "metadata": "metadata or {}",
}
```

### tracker -> client
#### Success
```json
{
    "status": "success",
    "message": "Peer registered successfully",
    "peer_id": "peer_id",
    "ip": "ip",
    "port": "port"
}
```
## 「GET /get-list」
### tracker -> client
```json
{
	"status": "success",
	"message": "Retrieved peer list successfully",
	"count": 1,
	"peers": [
		{
			"peer_id": "alice",
			"ip": "127.0.0.1",
			"port": 7001,
			"metadata": {},
			"status": "active"
		}
	]
}
```
