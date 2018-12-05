if [ "$1" = "post" ]; then
	curl -x socks5h://localhost:7000 -i -N \
		--include --no-buffer \
		--header "Connection: Upgrade" \
		--header "Upgrade: websocket" \
		--header "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
		--header "Sec-WebSocket-Version: 13" \
		-d "username=foo&password=bar" \
		-X POST http://x6lwrc5juitjntcc.onion
else
	curl -x socks5h://localhost:7000 -i -N \
		--include --no-buffer \
		--header "Connection: Upgrade" \
		--header "Upgrade: websocket" \
		--header "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
		--header "Sec-WebSocket-Version: 13" \
		http://x6lwrc5juitjntcc.onion/websocket
fi

