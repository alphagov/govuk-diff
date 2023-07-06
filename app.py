import pathlib
import pygit2
import io
import subprocess
import urllib.request
import json
from flask import Flask, render_template, request

app = Flask(__name__)

repo_path = pathlib.Path("../gitgovuk") # The repo needs an initial commit before this script can commit
repo = pygit2.Repository(repo_path)

def chunks(log, lines=3):
    buf = io.StringIO(log)
    while chunk := buf.readline():
        for _ in range(lines - 1):
            chunk += buf.readline()
        yield chunk


def parse_log(log):
    entries = chunks(log)
    list_of_log_lines = [entry.splitlines() for entry in entries]
    transpose = list(map(list, zip(*list_of_log_lines))) # transpose list
    return transpose


def git_log_of_file(file_path):
    ret = subprocess.run([
        "git log --pretty=tformat:\"%h%n%ci%n%s\" --date=iso",
        file_path
    ], cwd=repo_path, capture_output=True, shell=True)
    return parse_log(ret.stdout.decode())


def file_path_from_content_id(content_id):
    file_name = content_id
    # Create a directory hierarchy using the first few characters of the
    # content_id, so that not every file is in the same folder, which
    # would make it very hard to browse.
    dir = pathlib.Path(*list(file_name[:4]))
    repo_dir = pathlib.Path(repo_path, dir)
    dir_file = pathlib.Path(dir, file_name)
    repo_dir_file = pathlib.Path(repo_dir, file_name)
    return dir_file


def content_api_from_url(url):
    return url.replace("https://www.gov.uk/", "https://www.gov.uk/api/content/")


def content_id_of_url(url):
    with urllib.request.urlopen(content_api_from_url(url)) as req:
        content_json = json.load(req)
        return content_json['content_id']


def file_path_from_url(url):
    return file_path_from_content_id(content_id_of_url(url))


@app.route('/')
def my_form(methods=['GET']):
    return render_template('diff2htmlui.html', url='Paste GOV.UK URL here', diff='', diffs=[])

@app.route('/', methods=['POST'])
def my_form_post():
    url = request.form['url']
    file_path = file_path_from_url(url)
    git_log = git_log_of_file(file_path)
    # diff = repo.diff('HEAD~1', 'HEAD')
    return render_template(
        'diff2htmlui.html',
        # diff=diff.patch,
        url=url,
        diffs=git_log[0]
    )
