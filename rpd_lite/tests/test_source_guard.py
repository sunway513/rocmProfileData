"""T1 — Source-level dependency guard tests.

Verify rpd_lite source code has no references to roctracer or rocprofiler-sdk.
These tests run without any build or GPU — pure file inspection.
"""
import os
import re

RPDB_LITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_FILES = []
for f in os.listdir(RPDB_LITE_DIR):
    if f.endswith((".cpp", ".h")):
        SOURCE_FILES.append(os.path.join(RPDB_LITE_DIR, f))


class TestSourceGuard:
    """T1.x — No forbidden dependencies in source."""

    def test_no_roctracer_includes(self):
        """T1.2a — No #include of roctracer headers."""
        for fpath in SOURCE_FILES:
            with open(fpath) as f:
                content = f.read()
            matches = re.findall(r'#include\s*[<"].*roctracer.*[>"]', content)
            assert not matches, (
                f"{os.path.basename(fpath)} includes roctracer: {matches}"
            )

    def test_no_rocprofiler_sdk_includes(self):
        """T1.2b — No #include of rocprofiler-sdk headers."""
        for fpath in SOURCE_FILES:
            with open(fpath) as f:
                content = f.read()
            matches = re.findall(r'#include\s*[<"].*rocprofiler-sdk.*[>"]', content)
            assert not matches, (
                f"{os.path.basename(fpath)} includes rocprofiler-sdk: {matches}"
            )

    def test_no_roctracer_link_in_makefile(self):
        """T1.2c — Makefile does not link roctracer or rocprofiler-sdk."""
        makefile = os.path.join(RPDB_LITE_DIR, "Makefile")
        with open(makefile) as f:
            content = f.read()
        assert "-lroctracer" not in content, "Makefile links roctracer"
        assert "-lrocprofiler-sdk" not in content, "Makefile links rocprofiler-sdk"
        assert "-lroctx64" not in content, "Makefile links roctx64"

    def test_no_roctracer_symbols_in_source(self):
        """T1.2d — No roctracer API calls in non-comment code."""
        forbidden = [
            "roctracer_enable",
            "roctracer_disable",
            "roctracer_set_properties",
        ]
        for fpath in SOURCE_FILES:
            with open(fpath) as f:
                lines = f.readlines()
            for lineno, line in enumerate(lines, 1):
                stripped = line.strip()
                # Skip comments and blank lines
                if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                    continue
                for sym in forbidden:
                    assert sym not in line, (
                        f"{os.path.basename(fpath)}:{lineno} calls forbidden symbol: {sym}"
                    )

    def test_required_files_exist(self):
        """Verify all expected rpd_lite source files are present."""
        expected = [
            "rpd_lite.h",
            "rpd_lite.cpp",
            "hsa_intercept.cpp",
            "roctx_shim.cpp",
            "hip_intercept.cpp",
            "Makefile",
            "rpd_lite.sh",
            "rpd2trace.py",
        ]
        for fname in expected:
            fpath = os.path.join(RPDB_LITE_DIR, fname)
            assert os.path.exists(fpath), f"Missing file: {fname}"

    def test_rpd_lite_sh_is_executable(self):
        """rpd_lite.sh should have execute permission."""
        sh = os.path.join(RPDB_LITE_DIR, "rpd_lite.sh")
        assert os.access(sh, os.X_OK), "rpd_lite.sh is not executable"
