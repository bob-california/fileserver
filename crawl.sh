curl -H "Content-Type: application/json" \
    -X POST \
    --data '{"path":"'$1'"}' \
    http://localhost:80/crawl
