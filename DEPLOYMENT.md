# Public deployment on Render

This Blueprint deploys two public services from this repository:

- `trinetra-api`: FastAPI backend, with OpenAPI documentation at `/docs`
- `trinetra-web`: React single-page application

## Deploy

1. Sign in to [Render](https://dashboard.render.com/).
2. Select **New**, then **Blueprint**.
3. Connect `Dachepally-Sheshank/Fake-identity-and-document-screening`.
4. Render detects `render.yaml`. Review the two services and select **Apply**.
5. Wait for both deployments to finish, then open the public URL for `trinetra-web`.

Each push to `main` triggers a deployment.

## Prototype limitation

The hosted configuration uses SQLite for a simple demo. Uploaded synthetic files and history are not durable across restarts or redeployments. Use PostgreSQL and object storage before production. Never upload real identity documents.
