# GOV.UK content as a git repository

An experiment to make every version of every page on GOV.UK into a git commit.
This would facilitate tasks such as:

- See what changed since a given time (`git diff`)
- When, why and how was a certain line of content last edited (`git blame`).
- Find all edits that involved a certain string (`git log -G"His Majesty|Her Majesty" --patch`).
- Browse the site at a certain version (`git checkout`)

- [Trello](https://trello.com/c/kqgNh9Rn/20-open-version-history-of-govuk)
- [Google doc](https://docs.google.com/document/d/1VbBnYDUzCAE1dYghOoocsyDnpy6SssiqK4eywoyShSg)

## What we managed to do in the end

- This repo, and a repo https://github.com/alphagov/gitgovuk to contain the
  content commits.
- About 80k commits of content of document types `guide`, `detailed_guide`, and
  `travel_advice`, beginning with the present day and working back in time.
  That was over a year of changes.
- All document types except `step_by_step` that existed in November 2022,
  because we based our queries on
  https://github.com/alphagov/govuk-knowledge-graph-gcp, which was complete in
  that month, but is now out of date, and doesn't do historic document types.
- No API endpoints
- A streamlit app that runs on a laptop, and is hardcoded to certain file paths.
- An interface for a bespoke kind of `git blame`, displaying the change note
  upon mouseover of the line of content that was changed.

## What we didn't manage to do

- Complete history (from the Publishing API database, so only back to 2017)
- API
- Incremental updates from the nightly GOV.UK Publishing API database backup
  file
- Historic document schemas, and versions of them
- Document `title` and `description` elements, and some other fields that could
  be considered to be content, such as `start_button_text`.
- Links.  We had hoped to include the structure of GOV.UK.
- Deletions of whole content items.

## Running the things

Restore a nightly backup of the GOV.UK Publishing API database, and run the
query in ./changes.sql to create a table called `commits`.

Create a directory alongside this repo, called `gitgovuk`, open a terminal
inside it, and run:

```sh
git init
scalar register
```

Install some python packages.

```sh
pip install "psycopg[binary]"
pip install pygit2
```

Run the python script `commit.py`.

```sh
python commit.py
```

It will begin making commits to the git repository in the `gitgovuk` directory,
and tell you how many commits have been made so far.  When you have lost
patience, stop the script.

Run the streamlit app.

```sh
streamlit run diffgovuk.py
```

## Gif of git repo search

![Animated gif of using the streamlit app](./streamlit.gif)

## Potential API endpoints

`https://diff.gov.uk/<endpoint>`

- `/diff` previous edition
- `/diff/[n]` nth edition
- `/diff/-[n]` nth previous edition
- `/diff/:hash` or `/diff/edition_id` specific edition
- `/diff/yyyy-mm-ddThh:mm:ss` edition current at that time
- `/diff/:hash/:hash` or `/diff/:edition_id/:edition_id` between two particular editions (infer which is newer)
- `/diff/:hash/yyyy-mm-dd` etc.
- `/diffs` list editions, datetime, severity and diff
- `/diffs?neighbours=true` include editions, datetime, severity and diff of links from/to the `page,` to visualise as a timeline
- `/blame` for each line, show the edition that last edited it e.g. `https://publisher.staging.publishing.service.gov.uk/editions/646c9126f7a41d000c29ab0b/history#body28` is the notes of the 28th edition (of that content item)
- `/links/to` URLs that the page links to, datetime and severity of their last update, datetime of their last public update
- `/links/from` URLs that link to the page
- `/diffs/search?keywords=foo+bar` filter url/diffs for diffs that affect all the given keywords
- `/diffs/search?keywords=foo+bar&keywords=baz` diffs that affect all of at least one set of keywords

## Potential interface

Browse to an endpoint to see the unrendered govspeak or HTML, with diff
highlighting.

## Potential implementation

- Git, but it might not scale well, so https://git-scm.com/docs/scalar `scalar
  register`
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

- [x] How many characters of the content ID are nearly unique? _Four_.
- [x] How long does `git checkout <commit>` take? _Less than a second, with 80k
  commits_.
- [x] How long does `git blame` take? _Several seconds, with 80k commits_.
- [] Find the thing for browsing Git repos. _Couldn't find it_.
- [x] `git commit` with a specific timestamp.
- [ ] Understand CRUD of documents via editions.
- [ ] Understand which of GONE and other similar statuses should be implemented by deleting the file.
- [ ] Find out how the right to be forgotten is managed on GOV.UK and with the
  National Archives.

## Cloud SQL Postgres

This took 16 hours to restore the 30GB Publishing API database backup file, so
we abandoned it.  The [GOV.UK Knowledge
Graph](https://github.com/alphagov/govuk-knowledge-graph-gcp) can restore it in
about an hour, by disabling some protections against data corruption, such as
write-ahead-logging, and using an SSD drive directly connected to the instance
(instead of over the network).

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

## Learnings

- GCP Cloud SQL (Postgres) took 16 hours to restore the 30G publishing database
  from backup.  Most of that was the largest table: `editions`.  It turns out
  that heavily optimising the same task in the
  https://github.com/alphagov/govuk-knowledge-graph-gcp was well worth it -- it
  takes only about an hour there, because the compute instance has a direct
  connection to an SSD disk (instead of a network connection), and postgres is
  configured not to take any preventative measures against data corruption (no
  write-ahead log, etc.).
- Flask is very fiddly if you want form elements to stay in sync.  Streamlit is
  much easier, and you don't even have to write an HTML template.
- The Publishing API database has lots of duplicate editions, where absolutely
  nothing changed.  These are probably created when a rendering app is updated,
  and all the documents of a certain type are republished in order to cause the
  rendering app to re-render them.
- Git scales pretty well, but not that well.  Above 80k commits, it could only
  make 10-15 commits per second.  `git log <filename>` is also pretty slow.  We
  could do better by parsing `git log` into a database, which could be indexed
  by filename.
- It was worthwhile to use the first four characters of a `content_id` as
  a directory hierarchy, so that the repo can be browsed, rather than have
  hundreds of thousands of files in a single directory.
- Editions of mainstream pages don't have change notes.
- Data protection would take some care -- the third-most changed page (among
  `guide`, `detailed_guide` and `travel_advice` is a [list of upcoming
  disciplinary hearings of
  schoolteachers](https://www.gov.uk/guidance/teacher-misconduct-attend-a-professional-conduct-panel-hearing-or-meeting),
  naming the people involved.
- Legislation.gov.uk makes it possible to explore 1000 years of the history of
  law.
