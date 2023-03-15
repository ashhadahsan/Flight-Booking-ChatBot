# pneuma-ai
 
https://aws.amazon.com/getting-started/hands-on/serve-a-flask-app/

docker build -t ai-backend .
docker run -p 80:80 ai-backend

aws lightsail push-container-image --service-name backend-imagegenerator-ai --label image-gen --image image-gen

aws lightsail create-container-service-deployment --service-name backend-imagegenerator-ai --containers file://containers.json --public-endpoint file://public-endpoint.json

