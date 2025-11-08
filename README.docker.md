# Docker development instructions

This project includes a development Docker setup that runs both Django and Vite (npm run dev) in one container.

Files added:
- `Dockerfile` — builds an image with Python 3.13 and Node installed, installs Python and Node deps.
- `docker-entrypoint.sh` — starts `npm run dev` (Vite) and `python manage.py runserver` in the container.
- `docker-compose.yml` — convenient dev service that maps ports 8000 and 5173 and mounts the project.

Quick start (build and run):

```bash
# Build and start the dev container
docker compose up --build
```

The Django dev server will be available at http://localhost:8000 and Vite at http://localhost:5173.

Notes and assumptions:
- The Docker setup installs Python dependencies listed in `pyproject.toml` by directly pinning the same requirements in the Dockerfile. If you move to Poetry or another workflow, update the Dockerfile accordingly.
- Database is expected to be hosted externally (Heroku). The container does not create a local DB by default. If you need to point to your Heroku Postgres, set `DATABASE_URL` environment variable when starting the container.
- To keep DaisyUI and other Tailwind/Vite dev plugins available during development, `npm ci` is run in the image and `node_modules` is preserved inside the container (the compose file mounts `/app/node_modules` as an anonymous volume to avoid being overwritten by host mounts).

Troubleshooting:
- If Vite fails to start because of port conflicts, ensure nothing else is listening on 5173 on the host, or change the port mapping in `docker-compose.yml`.
- If your local code changes don't reflect in Vite, ensure files are mounted (`volumes:` in compose) and that `node_modules` isn't clobbered by a host directory.
