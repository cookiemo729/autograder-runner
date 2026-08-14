import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from autograde.models import GradeResult, TestResult


class VueEngine:
    """
    Grade a Vue/Vite project using pnpm and hidden Vitest tests.

    Design:
      1. Copy the student project to an isolated temporary folder.
      2. Install dependencies once, using persistent Docker pnpm caches.
      3. Build once in a network-disabled container.
      4. Run ALL hidden Vitest tests in ONE network-disabled container.
      5. Parse Vitest's JSON report into normal AutoGrade TestResult objects.

    This avoids starting one Docker/Vitest process per testcase, which is
    especially slow on Docker Desktop / Windows bind mounts.
    """

    DOCKER_IMAGE = "node:22"

    PNPM_STORE_VOLUME = "autograde-pnpm-store"
    COREPACK_CACHE_VOLUME = "autograde-corepack-cache"

    VITEST_RESULT_FILE = "autograde-vitest-results.json"

    def grade(self, assignment, submission_folder):
        submission_folder = Path(submission_folder)
        tests = assignment.get("testcases", [])
        max_score = sum(test["points"] for test in tests)

        work_folder = Path(
            tempfile.mkdtemp(prefix="vue-grade-")
        )

        try:
            print(
                "Preparing Vue grading environment...",
                flush=True,
            )

            missing = self._missing_required_files(
                submission_folder,
                assignment.get("required_files", []),
            )

            if missing:
                print(
                    "=== Missing required Vue project files ==="
                )
                for filename in missing:
                    print(filename)

                return self._all_failed(
                    tests,
                    max_score,
                )

            self._copy_project(
                submission_folder,
                work_folder,
            )

            assignment_folder = Path(
                assignment["_assignment_folder"]
            )

            hidden_test = (
                assignment_folder
                / assignment["test_file"]
            )

            shutil.copy2(
                hidden_test,
                work_folder / hidden_test.name,
            )

            # ------------------------------------------------------
            # 1. Install dependencies once.
            # ------------------------------------------------------
            print()
            print(
                "Installing dependencies with pnpm...",
                flush=True,
            )
            print(
                "(The first run may take several minutes; "
                "later runs reuse the pnpm cache.)",
                flush=True,
            )

            install_command = self._docker_command(
                work_folder,
                network_enabled=True,
                use_package_cache=True,
            ) + [
                "bash",
                "-lc",
                (
                    "set -e; "
                    "export COREPACK_HOME=/corepack; "
                    "corepack enable; "
                    "echo \"pnpm version: $(pnpm --version)\"; "
                    "pnpm config set store-dir /pnpm/store; "
                    "pnpm install "
                    "--frozen-lockfile "
                    "--ignore-scripts "
                    "--reporter=append-only"
                ),
            ]

            install_timeout = assignment.get(
                "install_timeout",
                600,
            )

            try:
                install_result = subprocess.run(
                    install_command,
                    timeout=install_timeout,
                )

            except subprocess.TimeoutExpired:
                print()
                print(
                    "=== pnpm install timed out "
                    f"after {install_timeout} seconds ==="
                )

                return self._all_failed(
                    tests,
                    max_score,
                )

            if install_result.returncode != 0:
                print()
                print("=== pnpm install failed ===")

                return self._all_failed(
                    tests,
                    max_score,
                )

            print()
            print(
                "Dependencies installed.",
                flush=True,
            )

            # ------------------------------------------------------
            # 2. Build once.
            # ------------------------------------------------------
            build_test = next(
                (
                    test
                    for test in tests
                    if test["id"] == "build"
                ),
                None,
            )

            results_by_id = {}
            score = 0

            if build_test is not None:
                print(
                    "Building Vue application...",
                    flush=True,
                )

                build_timeout = build_test.get(
                    "timeout",
                    assignment.get(
                        "build_timeout",
                        90,
                    ),
                )

                start = time.perf_counter()

                build_command = self._docker_command(
                    work_folder,
                    network_enabled=False,
                    use_package_cache=True,
                ) + [
                    "bash",
                    "-lc",
                    "./node_modules/.bin/vite build",
                ]

                try:
                    build_result = subprocess.run(
                        build_command,
                        capture_output=True,
                        text=True,
                        timeout=build_timeout,
                    )

                    elapsed = (
                        time.perf_counter()
                        - start
                    )

                    build_passed = (
                        build_result.returncode == 0
                    )

                    print(
                        f"{build_test['name']}: "
                        f"{elapsed:.3f}s"
                    )

                    if not build_passed:
                        if build_result.stdout:
                            print(build_result.stdout)

                        if build_result.stderr:
                            print(build_result.stderr)

                except subprocess.TimeoutExpired:
                    build_passed = False

                    print(
                        f"{build_test['name']}: "
                        "TIME LIMIT EXCEEDED "
                        f"({build_timeout}s)"
                    )

                results_by_id["build"] = build_passed

            # ------------------------------------------------------
            # 3. Run ALL component tests in ONE Vitest process.
            # ------------------------------------------------------
            component_tests = [
                test
                for test in tests
                if test["id"] != "build"
            ]

            if component_tests:
                print()
                print(
                    "Running hidden Vue tests "
                    "in a single Vitest session...",
                    flush=True,
                )

                result_path = (
                    work_folder
                    / self.VITEST_RESULT_FILE
                )

                if result_path.exists():
                    result_path.unlink()

                suite_timeout = assignment.get(
                    "test_suite_timeout",
                    120,
                )

                vitest_command = self._docker_command(
                    work_folder,
                    network_enabled=False,
                    use_package_cache=True,
                ) + [
                    "bash",
                    "-lc",
                    (
                        "./node_modules/.bin/vitest run "
                        f"{hidden_test.name} "
                        "--reporter=json "
                        f"--outputFile={self.VITEST_RESULT_FILE}"
                    ),
                ]

                start = time.perf_counter()

                try:
                    vitest_result = subprocess.run(
                        vitest_command,
                        capture_output=True,
                        text=True,
                        timeout=suite_timeout,
                    )

                    elapsed = (
                        time.perf_counter()
                        - start
                    )

                    print(
                        "Hidden Vue test suite: "
                        f"{elapsed:.3f}s"
                    )

                    parsed = self._read_vitest_results(
                        result_path
                    )

                    for test in component_tests:
                        passed = parsed.get(
                            test["id"],
                            False,
                        )

                        results_by_id[
                            test["id"]
                        ] = passed

                        status = (
                            "PASS"
                            if passed
                            else "FAIL"
                        )

                        print(
                            f"  {status}: "
                            f"{test['name']}"
                        )

                    # If Vitest failed before it could produce a
                    # report, print its diagnostics.
                    if (
                        not result_path.exists()
                        and vitest_result.returncode != 0
                    ):
                        print()
                        print(
                            "=== Vitest did not produce "
                            "a result file ==="
                        )

                        if vitest_result.stdout:
                            print(
                                vitest_result.stdout
                            )

                        if vitest_result.stderr:
                            print(
                                vitest_result.stderr
                            )

                except subprocess.TimeoutExpired:
                    print(
                        "Hidden Vue test suite: "
                        "TIME LIMIT EXCEEDED "
                        f"({suite_timeout}s)"
                    )

                    for test in component_tests:
                        results_by_id[
                            test["id"]
                        ] = False

            # ------------------------------------------------------
            # 4. Convert results back into normal AutoGrade results.
            # ------------------------------------------------------
            final_results = []

            for test in tests:
                passed = results_by_id.get(
                    test["id"],
                    False,
                )

                result = TestResult(
                    name=test["name"],
                    passed=passed,
                    points=test["points"],
                )

                final_results.append(result)

                if passed:
                    score += test["points"]

            return GradeResult(
                score=score,
                max_score=max_score,
                tests=final_results,
            )

        finally:
            shutil.rmtree(
                work_folder,
                ignore_errors=True,
            )

    def _read_vitest_results(
        self,
        result_path,
    ):
        """
        Vitest's JSON reporter is Jest-compatible enough for our use.
        Extract each assertion's leaf title and status.

        Returns:
            {
                "ex1_message": True,
                "ex1_fruits": True,
                ...
            }
        """
        if not result_path.exists():
            return {}

        try:
            data = json.loads(
                result_path.read_text(
                    encoding="utf-8"
                )
            )
        except (
            OSError,
            json.JSONDecodeError,
        ):
            return {}

        results = {}

        for test_file in data.get(
            "testResults",
            [],
        ):
            assertions = test_file.get(
                "assertionResults",
                [],
            )

            for assertion in assertions:
                title = assertion.get(
                    "title"
                )

                if not title:
                    # Some reporter versions expose the leaf
                    # name under ancestorTitles + fullName only.
                    full_name = assertion.get(
                        "fullName",
                        "",
                    )

                    if full_name:
                        title = (
                            full_name
                            .strip()
                            .split()[-1]
                        )

                if title:
                    results[str(title)] = (
                        assertion.get("status")
                        == "passed"
                    )

        return results

    def _missing_required_files(
        self,
        submission_folder,
        required_files,
    ):
        return [
            filename
            for filename in required_files
            if not (
                submission_folder
                / filename
            ).exists()
        ]

    def _copy_project(
        self,
        source,
        destination,
    ):
        ignored_names = {
            ".git",
            "node_modules",
            "dist",
            "coverage",
            "playwright-report",
            "test-results",
        }

        for item in source.iterdir():
            if item.name in ignored_names:
                continue

            target = destination / item.name

            if item.is_dir():
                shutil.copytree(
                    item,
                    target,
                    ignore=shutil.ignore_patterns(
                        *ignored_names
                    ),
                )
            else:
                shutil.copy2(
                    item,
                    target,
                )

    def _all_failed(
        self,
        tests,
        max_score,
    ):
        return GradeResult(
            score=0,
            max_score=max_score,
            tests=[
                TestResult(
                    name=test["name"],
                    passed=False,
                    points=test["points"],
                )
                for test in tests
            ],
        )

    def _docker_command(
        self,
        work_folder,
        network_enabled=False,
        use_package_cache=False,
    ):
        command = [
            "docker",
            "run",
            "--rm",
            "--memory",
            "1g",
            "--cpus",
            "1",
            "--pids-limit",
            "256",
            "-v",
            f"{work_folder.resolve()}:/work",
            "-w",
            "/work",
        ]

        if use_package_cache:
            command += [
                "-v",
                (
                    f"{self.PNPM_STORE_VOLUME}"
                    ":/pnpm/store"
                ),
                "-v",
                (
                    f"{self.COREPACK_CACHE_VOLUME}"
                    ":/corepack"
                ),
                "-e",
                "COREPACK_HOME=/corepack",
            ]

        if not network_enabled:
            command += [
                "--network",
                "none",
            ]

        command.append(
            self.DOCKER_IMAGE
        )

        return command
