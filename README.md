# FastAPI fileserver with SQLite

Simple file server used to get files in the file system based on their SHA-256 hash.

## Setup

In the `docker-compose.yaml` file, mount the desired files in the volume section.

Then adjust the `NUM_WORKERS` environment variable depending on your system. This variable is used to set the number of threads used for the SHA generation.

You can the build the docker image using:

```bash
docker-compose build
```

## Run

To run the server, just execute:

```bash
docker-compose up -d
```

If you wish to see the logs, execute:

```bash
docker-compose logs -f
```

## Use

The first time you launch the server, you will need to launch the crawler to generate the SHA-256 of every file you mounted. Simply use the script `crawl.sh` provided with argument the path to crawl (path inside the docker container).

For example: `./crawl.sh /data`

You can then request your file by SHA-256 with a GET request to the server. The route is `/files/{hash}`.

For example:

if you have a file with the following hash: `4a096987474a260c3376b92de288a67de3c73f74db4df8e2fc63ee7ce78005c4`, call `http://locahost:80/files/4a096987474a260c3376b92de288a67de3c73f74db4df8e2fc63ee7ce78005c4`

There is also a helper route `GET /files` to get the first 100 hash in your database.

> :warning: Remove this route for production
