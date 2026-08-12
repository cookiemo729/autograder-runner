import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from autograde.models import GradeResult, TestResult


class JavaEngine:

    DOCKER_IMAGE = "eclipse-temurin:17-jdk"

    def grade(self, assignment, submission_folder):

        submission_folder = Path(
            submission_folder
        )

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

            compile_command = (
                self._docker_command(
                    work_folder
                )
                + [
                    "javac",
                    *java_files,
                ]
            )

            try:

                compile_result = (
                    subprocess.run(
                        compile_command,
                        capture_output=True,
                        text=True,
                        timeout=assignment.get(
                            "compile_timeout",
                            10,
                        ),
                    )
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
                        )
                    ],
                )


            if (
                compile_result.returncode
                != 0
            ):

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

                return GradeResult(
                    score=0,
                    max_score=max_score,
                    tests=[
                        TestResult(
                            name="Compilation",
                            passed=False,
                            points=max_score,
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

                run_command = (
                    self._docker_command(
                        work_folder
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

                try:

                    run_result = (
                        subprocess.run(
                            run_command,
                            capture_output=True,
                            text=True,
                            timeout=timeout,
                        )
                    )

                    elapsed = (
                        time.perf_counter()
                        - start_time
                    )

                    output = (
                        run_result.stdout
                        .strip()
                    )

                    passed = (
                        run_result.returncode
                        == 0
                        and output == "PASS"
                    )

                    print(
                        f"{test['name']}: "
                        f"{elapsed:.6f}s"
                    )

                    if (
                        run_result.stderr
                    ):

                        print(
                            run_result.stderr
                        )

                except (
                    subprocess.TimeoutExpired
                ):

                    elapsed = (
                        time.perf_counter()
                        - start_time
                    )

                    passed = False

                    print(
                        f"{test['name']}: "
                        f"TIME LIMIT "
                        f"EXCEEDED "
                        f"({timeout}s)"
                    )


                result = TestResult(
                    name=test["name"],
                    passed=passed,
                    points=test["points"],
                )

                results.append(
                    result
                )

                if passed:
                    score += test[
                        "points"
                    ]


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


    def _docker_command(
        self,
        work_folder,
    ):

        return [
            "docker",
            "run",
            "--rm",

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