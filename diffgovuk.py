import streamlit as st
import streamlit.components.v1 as components
import pathlib
import pygit2
import io
import subprocess
import urllib.request
import json

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
    command = f"git log --pretty=tformat:\"%h%n%ci%n%s\" --date=iso {file_path}"
    ret = subprocess.run([command], cwd=repo_path, capture_output=True, shell=True)
    # print(ret)
    return parse_log(ret.stdout.decode())


def file_path_from_content_id(content_id):
    file_name = content_id
    # Create a directory hierarchy using the first few characters of the
    # content_id, so that not every file is in the same folder, which
    # would make it very hard to browse.
    dir = pathlib.Path(*list(file_name[:4]))
    repo_dir = pathlib.Path(repo_path, dir)
    dir_file = pathlib.Path(dir, file_name)
    st.session_state["dir_file"] = dir_file
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

def get_commits():
    file_path = file_path_from_url(st.session_state["url"])
    git_log = git_log_of_file(file_path)
    st.session_state["commits"] = [f"{a}  {b}  {c}" for a, b, c in zip(*git_log)]
    print(st.session_state["commits"])
    st.session_state["commit1"] = st.session_state["commits"][1]
    st.session_state["commit2"] = st.session_state["commits"][0]


def render_html(diff):
    html = """
        <!DOCTYPE html>
        <html lang="en-us">
          <head>
            <meta charset="utf-8" />
            <!-- Make sure to load the highlight.js CSS file before the Diff2Html CSS file -->
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.7.1/styles/github.min.css" />
            <link
              rel="stylesheet"
              type="text/css"
              href="https://cdn.jsdelivr.net/npm/diff2html/bundles/css/diff2html.min.css"
            />
            <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/diff2html/bundles/js/diff2html-ui.min.js"></script>
          </head>
          <script>
            const diffString = `""" + diff + """`;
            document.addEventListener('DOMContentLoaded', function () {
              var targetElement = document.getElementById('myDiffElement');
              var configuration = {
                drawFileList: true,
                fileListToggle: false,
                fileListStartVisible: false,
                fileContentToggle: false,
                matching: 'lines',
                outputFormat: 'line-by-line',
                synchronisedScroll: true,
                highlight: true,
                renderNothingWhenEmpty: false,
              };
              var diff2htmlUi = new Diff2HtmlUI(targetElement, diffString, configuration);
              diff2htmlUi.draw();
              diff2htmlUi.highlightCode();
            });
          </script>
          <body>
            <div id="myDiffElement"></div>
          </body>
        </html>
    """
    # print(html)
    return html


def commit_from_selectbox_value(s):
    return s.split(None, 1)[0]


def change_note_from_selectbox_value(s):
    if s != "":
        return s.split(None, 4)[4]
    else:
        return ""


def diff_of_commits():
    commit1 = commit_from_selectbox_value(st.session_state["commit1"])
    commit2 = commit_from_selectbox_value(st.session_state["commit2"])
    command = f"""git diff --no-prefix -U1000000 {commit1} {commit2} {st.session_state["dir_file"]}"""
    # print(command)
    ret = subprocess.run(command, cwd=repo_path, capture_output=True, shell=True)
    return ret.stdout.decode()


def show_diff():
    diff = diff_of_commits()
    st.session_state["diff"] = render_html(diff)


st.title('diff.gov.uk')

# Check if 'key' already exists in session_state
# If not, then initialize it
if "url" not in st.session_state:
    st.session_state["url"] = ""

if "commits" not in st.session_state:
    st.session_state["commits"] = []

if "commit1" not in st.session_state:
    st.session_state["commit1"] = ""

if "commit2" not in st.session_state:
    st.session_state["commit2"] = ""

if "diff" not in st.session_state:
    st.session_state["diff"] = ""

if "dir_file" not in st.session_state:
    st.session_state["dir_file"] = ""

st.text_input("Enter a GOV.UK URL:", key="url", on_change=get_commits)

st.selectbox("Earlier commit", options=st.session_state["commits"], key="commit1")
st.selectbox("Later commit", options=st.session_state["commits"], key="commit2")

st.button('Show diff', on_click=show_diff)

st.write(change_note_from_selectbox_value(st.session_state["commit2"]))

components.html(st.session_state["diff"], height=10000, width = 10000, scrolling=True)
