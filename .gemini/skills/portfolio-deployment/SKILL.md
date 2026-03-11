---
name: portfolio-deployment
description: Instructions for building and launching the portfolio website.
---

# Portfolio Deployment

The portfolio is a web application located in the `portfolio/` directory that displays resumes and CV data.

## Launching the Portfolio

Use the VS Code task "Build and Launch Portfolio" or run the following command:

```bash
cd portfolio && \
rm -rf data && \
mkdir -p data && \
cp -r ../resumes data/ && \
cp -r ../cv-data data/ && \
docker compose up --build --force-recreate
```

## How it works
1. **Data Sync:** It copies the latest `cv-data/resumes/` and `cv-data/` into the `portfolio/data/` directory.
2. **Docker Compose:** Starts the Next.js application using Docker.
3. **Hot Reload:** The application should reflect changes made to the data after a rebuild.

