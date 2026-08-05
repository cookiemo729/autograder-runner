import hashlib
import hmac
import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, request

from runner import grade_assignment


app = Flask(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent
DATABASE_PATH = PROJECT_ROOT / "autograder.db"

ASSIGNMENTS = {
    "wk1ex4": PROJECT_ROOT / "examples" / "wk1ex4",
}

ALLOWED_REPOSITORIES = {
    "cookiemo729/wk1ex4-student-template",
}

AUTOGRADER_API_KEY = os.environ.get("AUTOGRADER_API_KEY")


def get_database():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_database() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repository TEXT NOT NULL,
                assignment TEXT NOT NULL,
                commit_sha TEXT NOT NULL,
                score INTEGER NOT NULL,
                max_score INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                tests_json TEXT NOT NULL,
                submitted_at TEXT NOT NULL,
                UNIQUE(repository, assignment, commit_sha)
            )
            """
        )


def save_result(
    repository,
    assignment,
    commit_sha,
    score,
    max_score,
    passed,
    tests,
):
    submitted_at = datetime.now(timezone.utc).isoformat()

    with get_database() as connection:
        connection.execute(
            """
            INSERT INTO submissions (
                repository,
                assignment,
                commit_sha,
                score,
                max_score,
                passed,
                tests_json,
                submitted_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(repository, assignment, commit_sha)
            DO UPDATE SET
                score = excluded.score,
                max_score = excluded.max_score,
                passed = excluded.passed,
                tests_json = excluded.tests_json,
                submitted_at = excluded.submitted_at
            """,
            (
                repository,
                assignment,
                commit_sha,
                score,
                max_score,
                int(passed),
                json.dumps(tests),
                submitted_at,
            ),
        )


def get_latest_submissions():
    with get_database() as connection:
        return connection.execute(
            """
            SELECT
                repository,
                assignment,
                commit_sha,
                score,
                max_score,
                passed,
                submitted_at
            FROM submissions
            ORDER BY submitted_at DESC
            LIMIT 100
            """
        ).fetchall()


def format_submission_time(utc_string):

    utc_time = datetime.fromisoformat(utc_string)

    sg_time = utc_time.astimezone(
        ZoneInfo("Asia/Singapore")
    )

    now = datetime.now(
        ZoneInfo("Asia/Singapore")
    )

    if sg_time.date() == now.date():
        return "Today " + sg_time.strftime("%I:%M %p")

    if sg_time.date() == (
        now.date() - timedelta(days=1)
    ):
        return "Yesterday " + sg_time.strftime("%I:%M %p")

    return sg_time.strftime(
        "%d %b %Y %I:%M %p"
    )

@app.get("/")
def home():
    submissions = get_latest_submissions()

    rows = []

    for submission in submissions:

        passed = bool(submission["passed"])

        status_text = "Passed" if passed else "Failed"
        status_class = "passed" if passed else "failed"

        student = submission["repository"].split("/")[0]

        display_time = format_submission_time(
            submission["submitted_at"]
        )

        score_ratio = (
            submission["score"]
            / submission["max_score"]
            if submission["max_score"] > 0
            else 0
        )

        if score_ratio == 1:
            score_class = "score-full"
            score_icon = "●"
        elif score_ratio > 0:
            score_class = "score-partial"
            score_icon = "●"
        else:
            score_class = "score-zero"
            score_icon = "●"

        display_time = format_submission_time(
            submission["submitted_at"]
        )
        passed = bool(submission["passed"])
        status_text = "Passed" if passed else "Failed"
        status_class = "passed" if passed else "failed"
        student = submission["repository"].split("/")[0]

        rows.append(
            f"""
            <tr>
                <td>{student}</td>

                <td>{submission["assignment"]}</td>

                <td>
                    <span class="score-badge {score_class}">
                        {score_icon}
                        {submission["score"]}/{submission["max_score"]}
                    </span>
                </td>

                <td>
                    <span class="status {status_class}">
                        {status_text}
                    </span>
                </td>

                <td>
                    <code>{submission["commit_sha"][:7]}</code>
                </td>

                <td>{display_time}</td>
            </tr>
            """
        )

    if rows:
        table_body = "\n".join(rows)
    else:
        table_body = """
        <tr>
            <td colspan="6" class="empty">
                No submissions have been recorded yet.
            </td>
        </tr>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>AutoGrade Dashboard</title>

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 40px 20px;
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            color: #1f2937;
        }}

        .container {{
            max-width: 1200px;
            margin: auto;
        }}

        h1 {{
            margin-bottom: 5px;
        }}

        .subtitle {{
            color: #6b7280;
            margin-bottom: 30px;
        }}

        .card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }}

        .card-header {{
            padding: 20px 24px;
            border-bottom: 1px solid #e5e7eb;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th,
        td {{
            padding: 15px 18px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}

        th {{
            background: #f9fafb;
            color: #4b5563;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        .status {{
            display: inline-block;
            padding: 5px 11px;
            border-radius: 999px;
            font-size: 0.88rem;
            font-weight: bold;
        }}

        .passed {{
            background: #dcfce7;
            color: #166534;
        }}

        .failed {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .score-badge {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 5px 11px;
            border-radius: 999px;
            font-weight: bold;
        }}

        .score-full {{
            background: #dcfce7;
            color: #166534;
        }}

        .score-partial {{
            background: #fef3c7;
            color: #92400e;
        }}

        .score-zero {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .empty {{
            text-align: center;
            color: #6b7280;
            padding: 40px;
        }}

        code {{
            background: #f3f4f6;
            padding: 3px 6px;
            border-radius: 5px;
        }}

        @media (max-width: 850px) {{
            .card {{
                overflow-x: auto;
            }}

            table {{
                min-width: 900px;
            }}
        }}
    </style>
</head>

<body>
    <div class="container">
        <h1>AutoGrade</h1>

        <div class="subtitle">
            Instructor submission dashboard
        </div>

        <div class="card">
            <div class="card-header">
                <strong>Latest submissions</strong>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Student</th>
                        <th>Assignment</th>
                        <th>Score</th>
                        <th>Status</th>
                        <th>Commit</th>
                        <th>Submitted</th>
                    </tr>
                </thead>

                <tbody>
                    {table_body}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/grade")
def grade():
    supplied_key = request.headers.get("X-Autograder-Key", "")

    if not AUTOGRADER_API_KEY:
        return jsonify({
            "error": "Server API key is not configured"
        }), 500

    if not hmac.compare_digest(
        supplied_key,
        AUTOGRADER_API_KEY,
    ):
        return jsonify({
            "error": "Unauthorized"
        }), 401

    data = request.get_json(silent=True) or {}

    assignment_key = data.get("assignment")
    repository_name = data.get("repository")
    commit_sha = data.get("commit_sha")

    if not assignment_key:
        return jsonify({"error": "Missing assignment"}), 400

    if not repository_name:
        return jsonify({"error": "Missing repository"}), 400

    if not commit_sha:
        return jsonify({"error": "Missing commit_sha"}), 400

    assignment_path = ASSIGNMENTS.get(assignment_key)

    if assignment_path is None:
        return jsonify({"error": "Unknown assignment"}), 400

    if repository_name not in ALLOWED_REPOSITORIES:
        return jsonify({
            "error": "Repository is not allowed"
        }), 403

    repository_url = (
        f"https://github.com/{repository_name}.git"
    )

    work_folder = Path(
        tempfile.mkdtemp(prefix="autograde-")
    )

    submission_folder = work_folder / "submission"

    try:
        clone_result = subprocess.run(
            [
                "git",
                "clone",
                "--no-checkout",
                repository_url,
                str(submission_folder),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if clone_result.returncode != 0:
            return jsonify({
                "error": "Unable to clone repository",
                "details": clone_result.stderr,
            }), 400

        checkout_result = subprocess.run(
            [
                "git",
                "-C",
                str(submission_folder),
                "checkout",
                "--detach",
                commit_sha,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if checkout_result.returncode != 0:
            return jsonify({
                "error": "Unable to check out commit",
                "details": checkout_result.stderr,
            }), 400

        assignment, result = grade_assignment(
            str(assignment_path),
            str(submission_folder),
        )

        tests = [
            {
                "name": test.name,
                "passed": test.passed,
                "points": test.points,
                "awarded": (
                    test.points if test.passed else 0
                ),
            }
            for test in result.tests
        ]

        passed = result.score == result.max_score

        save_result(
            repository=repository_name,
            assignment=assignment_key,
            commit_sha=commit_sha,
            score=result.score,
            max_score=result.max_score,
            passed=passed,
            tests=tests,
        )

        return jsonify({
            "assignment": assignment_key,
            "title": assignment["title"],
            "repository": repository_name,
            "commit_sha": commit_sha,
            "score": result.score,
            "max_score": result.max_score,
            "passed": passed,
            "tests": tests,
        }), 200

    except subprocess.TimeoutExpired:
        return jsonify({
            "error": "Repository operation timed out"
        }), 408

    except Exception as error:
        app.logger.exception("Grading failed")

        return jsonify({
            "error": "Grading failed",
            "details": str(error),
        }), 500

    finally:
        shutil.rmtree(
            work_folder,
            ignore_errors=True,
        )


if __name__ == "__main__":
    initialize_database()

    app.run(
        host="127.0.0.1",
        port=8000,
    )