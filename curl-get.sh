# a curl client to test the websocket connection.
curl -x socks5h://localhost:7000 -i -N \
	--include --no-buffer \
	--header "Connection: Upgrade" \
	--header "Upgrade: websocket" \
	--header "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
	--header "Sec-WebSocket-Version: 13" \
	http://57t2u3lbegt27j7v.onion/websocket

