# GOV.UK content as a git repository

https://docs.google.com/document/d/1VbBnYDUzCAE1dYghOoocsyDnpy6SssiqK4eywoyShSg

[Trello](https://trello.com/c/kqgNh9Rn/20-open-version-history-of-govuk)

## Possible endpoints

`https://diff.gov.uk/<endpoint>`

- `/diff` previous edition
- `/diff/[n]` nth edition
- `/diff/-[n]` nth previous edition
- `/diff/:hash` specific edition
- `/diff/yyyy-mm-ddThh:mm:ss` edition current at that time
- `/diff/:hash/:hash` between two particular editions (infer which is newer)
- `/diff/:hash/yyyy-mm-dd` etc.
- `/diffs` list editions, datetime, severity and diff
- `/diffs?neighbours=true` include editions, datetime, severity and diff of links from/to the `page,` to visualise as a timeline
- `/blame` for each line, show the edition that last edited it e.g. `https://publisher.staging.publishing.service.gov.uk/editions/646c9126f7a41d000c29ab0b/history#body28` is the notes of the 28th edition (of that content item)
- `/links/to` URLs that the page links to, datetime and severity of their last update, datetime of their last public update
- `/links/from` URLs that link to the page
- `/diffs/search?keywords=foo+bar` filter url/diffs for diffs that affect all the given keywords
- `/diffs/search?keywords=foo+bar&keywords=baz` diffs that affect all of at least one set of keywords

## Interface

Browse to an endpoint to see the unrendered govspeak or HTML, with diff
highlighting.

## Implementation

- Git, but it might not scale well, so https://git-scm.com/docs/scalar
- Each file named by its content ID
- Files organised into a hierarchy by each of the first six (or however many) characters of the content ID
- Flask?
- [Generic GCP Project With Billing](https://console.cloud.google.com/welcome?project=generic-project-with-billing)

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
- Publisher is organised by content item.  This might actually simplify things.
- Interleaving changes from different tables (editions, links)

## Tasks

- [ ] Tasks
- [ ] How many characters of the content ID are nearly unique?
- [ ] How long does `git checkout <commit>` take?
- [ ] How long does `git blame` take?
- [ ] Find the thing for browsing Git repos
- [ ] `git commit` with a specific timestamp
- [ ] Understand CRUD of documents via editions
- [ ] Understand which of GONE and other similar statuses should be implemented by deleting the file

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

## Similar work

The Publisher app shows diffs between the current edition and the previous
edition.
https://github.com/alphagov/publisher/blob/main/app/views/editions/diff.html.erb

The diff is of the markdown
https://github.com/alphagov/publisher/blob/2490b437ea4c92653d7d7e9a0ad1b84c0fba869f/app/models/parted.rb#L31-L33
