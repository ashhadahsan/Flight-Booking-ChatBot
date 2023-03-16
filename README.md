# pneuma-ai
 
https://aws.amazon.com/getting-started/hands-on/serve-a-flask-app/

docker build -t ai-backend .
docker run -p 80:80 ai-backend

aws lightsail push-container-image --service-name ai-backend --label ai-backend --image ai-backend

aws lightsail create-container-service-deployment --service-name ai-backend --containers file://containers.json --public-endpoint file://public-endpoint.json

