import pathlib
from sys import stdout

# pip install "psycopg[binary]"
# Note: the module name is psycopg, not psycopg3
import psycopg

# pip install pygit2
import pygit2

repo_path = pathlib.Path("../gitgovuk") # The repo needs an initial commit before this script can commit
db_conn_string = "dbname=publishing_api_production user=postgres"
author_name = "Duncan Garmonsway"
author_email = "nacnudus@gmail.com"

repo = pygit2.Repository(repo_path)

index = repo.index
ref = repo.head.name

with psycopg.connect(db_conn_string) as conn:

    with conn.cursor(name = "commit") as cur: # Use of 'name' creates a server-side cursor

        cur.execute("SELECT * FROM commits;")

        commit_count = 0
        for record in cur:

            edition_id, content_id, updated_at, note, content = record

            file_name = str(content_id)
            # Create a directory hierarchy using the first few characters of the
            # content_id, so that not every file is in the same folder, which
            # would make it very hard to browse.
            dir = pathlib.Path(*list(file_name[:4]))
            repo_dir = pathlib.Path(repo_path, dir)
            dir_file = pathlib.Path(dir, file_name)
            repo_dir_file = pathlib.Path(repo_dir, file_name)

            repo_dir.mkdir(parents=True, exist_ok=True)

            with open(repo_dir_file, "w") as file:
                file.write(content)

            index.add(dir_file)
            index.write()

            message = f"Change note: {note}"

            author = pygit2.Signature(
                email=author_email,
                name=author_name,
                time=int(updated_at.timestamp())
            )

            parents = [repo.head.target]
            tree = index.write_tree()
            repo.create_commit(ref, author, author, message, tree, parents)

            commit_count += 1
            stdout.write(f"\rCommits: {commit_count}")
            stdout.flush();

stdout.write("\n")
stdout.flush();
