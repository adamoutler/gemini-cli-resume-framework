# Portfolio

This is a Next.js portfolio generated from your `cv-data` and `resumes`.

## Running Locally

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Building Docker Image

Because the data lives outside this directory (in `../resumes` and `../cv-data`), you must populate the `data` directory before building the Docker image context.

The application is configured to look in `../` first (for local dev), and then fallback to `./data/` (for Docker).

```bash
# Prepare data
mkdir -p data
cp -r ../resumes data/
cp -r ../cv-data data/

# Build and Run
docker build -t portfolio .
docker run -p 3000:3000 portfolio
```
