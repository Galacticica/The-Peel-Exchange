# W11 Containerizing an Application
By Reagan Zierke

## What process did you follow for creating the dockerfile?
I first had it pull the base python image. Then I had it install dependencies required to run the code along with Node.js and npm dependencies for frontend assets. Then I had it make the final command and cron bash files executable. Then I have it build and collect the frontend assets. Then it exposes the ports 8000 (backend) and 5173 (frontend). Then it sets the Django settings to conf.settings. Finally it runs the command ```/usr/local/bin/docker-entrypoint.sh``` which starts the application based on the DEBUG environment variable - in development mode it runs Django runserver and Vite dev server, while in production mode it runs gunicorn with database migrations and static file collection.

## What docker commands did you use to run the image?
I ran ```docker compose up --build``` to run it and then ran ```curl -I http://localhost:8000``` to test that it is running.