# persimmon-api





### troubleshooting


building the container on apple m1 is posing problems while deploying to gcp
```
docker buildx build --platform linux/amd64 -t myapp .
```


github actions gives warning while deploying,  but works from terminal
```
gcloud run deploy persimmon-api --region us-west2 --image gcr.io/persimmon-ai/persimmon-api:latest --port 8000 --platform "managed" --allow-unauthenticated
```
