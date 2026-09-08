import re
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

from autograde.models import GradeResult, TestResult


class JavaEngine:

    DOCKER_IMAGE = "eclipse-temurin:17-jdk"

    def grade(self, assignment, submission_folder):

        submission_folder = Path(submission_folder)

        tests = assignment.get(
            "testcases",
            [],
        )

        results = []
        score = 0

        max_score = sum(
            test["points"]
            for test in tests
        )

        work_folder = Path(
            tempfile.mkdtemp(
                prefix="java-grade-"
            )
        )

        try:

            # =========================
            # COPY STUDENT FILES
            # =========================

            for filename in assignment[
                "student_files"
            ]:

                source = (
                    submission_folder
                    / filename
                )

                if not source.exists():

                    return GradeResult(
                        score=0,
                        max_score=max_score,
                        tests=[
                            TestResult(
                                name=(
                                    "Missing file: "
                                    + filename
                                ),
                                passed=False,
                                points=max_score,
                                feedback=(
                                    f"Required file '{filename}' "
                                    "was not found in your submission. "
                                    "Check that the filename and "
                                    "capitalisation match the "
                                    "assignment requirements."
                                ),
                            )
                        ],
                    )

                shutil.copy2(
                    source,
                    work_folder / filename,
                )

            # =========================
            # COPY HIDDEN TEST
            # =========================

            assignment_folder = Path(
                assignment[
                    "_assignment_folder"
                ]
            )

            hidden_test = (
                assignment_folder
                / assignment["test_file"]
            )

            shutil.copy2(
                hidden_test,
                work_folder
                / hidden_test.name,
            )

            # =========================
            # JAVA FILES
            # =========================

            java_files = [
                path.name
                for path
                in work_folder.glob("*.java")
            ]

            # =========================
            # COMPILE INSIDE DOCKER
            # =========================

            compile_container = (
                self._new_container_name(
                    "compile"
                )
            )

            compile_command = (
                self._docker_command(
                    work_folder,
                    compile_container,
                )
                + [
                    "javac",
                    *java_files,
                ]
            )

            try:

                compile_result = subprocess.run(
                    compile_command,
                    capture_output=True,
                    text=True,
                    timeout=assignment.get(
                        "compile_timeout",
                        10,
                    ),
                )

            except subprocess.TimeoutExpired:

                print(
                    "=== Java compilation "
                    "timed out ==="
                )

                return GradeResult(
                    score=0,
                    max_score=max_score,
                    tests=[
                        TestResult(
                            name="Compilation",
                            passed=False,
                            points=max_score,
                            feedback=(
                                "Compilation exceeded the "
                                "allowed time limit. Check "
                                "your Java source files and "
                                "try again."
                            ),
                        )
                    ],
                )

            finally:

                self._remove_container(
                    compile_container
                )

            if compile_result.returncode != 0:

                print(
                    "=== Java compilation "
                    "failed ==="
                )

                print(
                    compile_result.stdout
                )

                print(
                    compile_result.stderr
                )

                feedback = (
                    self._compilation_feedback(
                        compile_result.stderr,
                        assignment["student_files"],
                        hidden_test.name,
                    )
                )

                return GradeResult(
                    score=0,
                    max_score=max_score,
                    tests=[
                        TestResult(
                            name="Compilation",
                            passed=False,
                            points=max_score,
                            feedback=feedback,
                        )
                    ],
                )

            # =========================
            # RUN TESTS
            # =========================

            for test in tests:

                timeout = test.get(
                    "timeout",
                    assignment.get(
                        "run_timeout",
                        5,
                    ),
                )

                container_name = (
                    self._new_container_name(
                        "test"
                    )
                )

                run_command = (
                    self._docker_command(
                        work_folder,
                        container_name,
                    )
                    + [
                        "java",
                        assignment[
                            "test_class"
                        ],
                        test["id"],
                    ]
                )

                start_time = (
                    time.perf_counter()
                )

                passed = False

                try:

                    run_result = subprocess.run(
                        run_command,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                    )

                    elapsed = (
                        time.perf_counter()
                        - start_time
                    )

                    output = (
                        run_result.stdout.strip()
                    )

                    passed = (
                        run_result.returncode == 0
                        and output == "PASS"
                    )

                    print(
                        f"{test['name']}: "
                        f"{elapsed:.6f}s"
                    )

                    if run_result.stderr:
                        print(
                            run_result.stderr
                        )

                except subprocess.TimeoutExpired:

                    elapsed = (
                        time.perf_counter()
                        - start_time
                    )

                    passed = False

                    print(
                        f"{test['name']}: "
                        f"TIME LIMIT EXCEEDED "
                        f"({timeout}s)"
                    )

                finally:

                    # Critical:
                    # guarantee that the Docker
                    # container and its Java
                    # process are destroyed.
                    self._remove_container(
                        container_name
                    )

                result = TestResult(
                    name=test["name"],
                    passed=passed,
                    points=test["points"],
                )

                results.append(result)

                if passed:
                    score += test["points"]

            return GradeResult(
                score=score,
                max_score=max_score,
                tests=results,
            )

        finally:

            shutil.rmtree(
                work_folder,
                ignore_errors=True,
            )

    # =========================
    # COMPILATION FEEDBACK
    # =========================

    def _compilation_feedback(
        self,
        stderr,
        student_files,
        hidden_test_name,
    ):

        if not stderr:
            return (
                "Your Java submission could not "
                "be compiled. Check your source "
                "files for syntax errors and make "
                "sure all required methods match "
                "the assignment specification."
            )

        # If javac reports an error involving the
        # hidden test, never expose the raw compiler
        # output because it may reveal private tests.
        if hidden_test_name in stderr:
            return (
                "Your submitted class does not "
                "match the required assignment "
                "interface. Check that all required "
                "methods from the starter code/"
                "specification are present and that "
                "their method names, parameters and "
                "return types have not been changed."
            )

        # Keep only compiler diagnostics that refer
        # to files submitted by the student.
        safe_lines = []
        include_following = False

        for line in stderr.splitlines():

            starts_student_error = any(
                re.match(
                    rf"^(?:.*/)?{re.escape(filename)}:"
                    r"\d+:\s*error:",
                    line,
                )
                for filename in student_files
            )

            if starts_student_error:
                safe_lines.append(line)
                include_following = True
                continue

            if include_following:

                # A new javac file diagnostic begins.
                if re.match(
                    r"^(?:.*/)?[^:]+\.java:"
                    r"\d+:\s*(?:error|warning):",
                    line,
                ):
                    include_following = False
                    continue

                # Do not expose anything mentioning
                # the private hidden test.
                if hidden_test_name in line:
                    include_following = False
                    continue

                # Keep a small amount of javac context:
                # source line, caret, symbol/location.
                if (
                    line.strip()
                    and not re.match(
                        r"^\d+\s+errors?$",
                        line.strip(),
                    )
                ):
                    safe_lines.append(line)

                # Limit how much compiler output is
                # returned to the student.
                if len(safe_lines) >= 8:
                    break

        if safe_lines:

            diagnostic = "\n".join(
                safe_lines[:8]
            )

            return (
                "Your Java submission could not "
                "be compiled.\n\n"
                + diagnostic
                + "\n\nPlease fix the compilation "
                "error and resubmit."
            )

        return (
            "Your Java submission could not "
            "be compiled. Check your source files "
            "for syntax/type errors and make sure "
            "all required methods match the "
            "assignment specification."
        )

    # =========================
    # CONTAINER NAME
    # =========================

    def _new_container_name(
        self,
        purpose,
    ):

        return (
            "autograde-java-"
            f"{purpose}-"
            f"{uuid.uuid4().hex}"
        )

    # =========================
    # REMOVE CONTAINER
    # =========================

    def _remove_container(
        self,
        container_name,
    ):

        subprocess.run(
            [
                "docker",
                "rm",
                "-f",
                container_name,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=False,
        )

    # =========================
    # DOCKER COMMAND
    # =========================

    def _docker_command(
        self,
        work_folder,
        container_name,
    ):

        return [
            "docker",
            "run",
            "--rm",

            # Give every grading container
            # a unique name so that we can
            # forcibly destroy it on timeout.
            "--name",
            container_name,

            # No internet access
            "--network",
            "none",

            # Maximum RAM
            "--memory",
            "256m",

            # Maximum CPU
            "--cpus",
            "1",

            # Prevent process explosion
            "--pids-limit",
            "64",

            # Mount temporary grading folder
            "-v",
            (
                f"{work_folder.resolve()}"
                ":/work"
            ),

            # Run commands here
            "-w",
            "/work",

            self.DOCKER_IMAGE,
        ]