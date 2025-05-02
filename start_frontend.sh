set -e

echo "Starting Textract Document Processor Frontend UI..."

cd "$(dirname "$0")/frontend"

python3 -m http.server 8080 &
SERVER_PID=$!

echo "Exposing frontend UI to the internet..."
PORT_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

if [ -z "$PORT_URL" ]; then
    echo "Starting ngrok tunnel..."
    ngrok http 8080 > /dev/null 2>&1 &
    NGROK_PID=$!
    
    sleep 3
    
    PORT_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
fi

echo "Frontend UI is now available at: $PORT_URL"
echo "Press Ctrl+C to stop the server"

trap "kill $SERVER_PID; [ ! -z \"$NGROK_PID\" ] && kill $NGROK_PID; echo 'Stopped frontend UI server'; exit 0" INT
wait
