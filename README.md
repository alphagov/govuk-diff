# GOV.UK content as a git repository

https://docs.google.com/document/d/1VbBnYDUzCAE1dYghOoocsyDnpy6SssiqK4eywoyShSg

## Logic

1. Sort events by datetime ascending.
2. Join `change_notes` and `documents`
3. Take a record
4. Extract the title and description
5. Extract the govspeak, or the HTML if the govspeak doesn't exist
6. Extract the most recent `change_notes.note`
7. Extract the `withdrawn_explanation`
8. Write some metadata to `<content_id>.json`
9. Write the content to `<content_id>`
10. Commit the files with a commit message that includes `update_type: <update_type>`

## Commit body

```text
title: <title>

description: <description>

<body>
```

## Include documents where

- `content_store` is anything
- `state <> 'draft'`
- `phase` is anything
- `left(document_type, 11) <> 'placeholder'`
- `locale = 'en'`

## Available metadata

### `state`

- `draft`
- `published`
- `unpublished`
- `superseded`

### `phase`

- `alpha`
- `beta`
- `live`

### `update_type`

- `minor`
- `republish`

### `content_store`

- `draft`
- `live`

### `redirects`

### `locale`

JSON, includes multiple redirections per document.

## Problems

- `change_notes` isn't distinct on `edition_id`, so choose the most recent note
  per edition.
- Tagging commits with metadata.  Could use git notes, but it's easier just to
  structure the commit message.
- Document schemas have changed over time.

## Cloud SQL Postgres

- https://console.cloud.google.com/sql/instances/publishing/overview?project=generic-project-with-billing
- https://cloud.google.com/sql/docs/postgres/connect-auth-proxy#unix-sockets

Discover the connectionName: `generic-project-with-billing:europe-west2:publishing`

```sh
gcloud sql instances describe --project generic-project-with-billing publishing
```

Prepare to connect to the database by running a clever-clogs proxy thingy.

```sh
sudo mkdir ./cloudsql; sudo chmod 777 ./cloudsql
./cloud-sql-proxy --unix-socket ./cloudsql generic-project-with-billing:europe-west2:publishing &
```

Connect to the default postgres database with psql.

```sh
psql "sslmode=disable host=/cloudsql/generic-project-with-billing:europe-west2:publishing user=postgres"
```

If the above doesn't work, then use tcp sockets instead

```sh
./cloud-sql-proxy --port 5432 generic-project-with-billing:europe-west2:publishing
psql "host=127.0.0.1 sslmode=disable dbname=postgres user=postgres"
```

Restore the publishing database from the backup file.

```sh
date
pg_restore \
  --verbose \
  --create \
  --clean \
  --no-owner \
  --jobs=2 \
  --dbname "host=127.0.0.1 sslmode=disable dbname=postgres user=postgres" \
  ./publishing-api-postgres_2023-07-03T05_00_01-publishing_api_production.gz
date
```
