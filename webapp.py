import hmac
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request

from runner import grade_assignment


app = Flask(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent

ASSIGNMENTS = {
    "wk1ex4": PROJECT_ROOT / "examples" / "wk1ex4",
}

ALLOWED_REPOSITORIES = {
    "cookiemo729/wk1ex4-student-template",
}

AUTOGRADER_API_KEY = os.environ.get("AUTOGRADER_API_KEY")


@app.get("/")
def home():
    return "AutoGrade API"


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

    if not hmac.compare_digest(supplied_key, AUTOGRADER_API_KEY):
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

        return jsonify({
            "assignment": assignment_key,
            "title": assignment["title"],
            "repository": repository_name,
            "commit_sha": commit_sha,
            "score": result.score,
            "max_score": result.max_score,
            "passed": result.score == result.max_score,
            "tests": [
                {
                    "name": test.name,
                    "passed": test.passed,
                    "points": test.points,
                    "awarded": (
                        test.points if test.passed else 0
                    ),
                }
                for test in result.tests
            ],
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
    app.run(
        host="127.0.0.1",
        port=8000,
    )