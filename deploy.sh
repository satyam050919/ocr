set -e

echo "Deploying Textract Document Processor API..."

echo "Building Docker image..."
docker build -t textract-processor:latest .

echo "Running Docker container..."
docker run -d -p 8000:8000 \
  -e AWS_REGION=${AWS_REGION:-us-east-1} \
  -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
  -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
  -e LOG_LEVEL=${LOG_LEVEL:-INFO} \
  --name textract-processor \
  textract-processor:latest

echo "Textract Document Processor API deployed successfully!"
echo "API is available at: http://localhost:8000"
echo "API documentation is available at: http://localhost:8000/docs"
