import sys
import subprocess


def _parse_args():
    return sys.argv[1:] or []


def run_format():
    subprocess.run(["bash", "scripts/format.sh", *_parse_args()])


def run_format_imports():
    subprocess.run(["bash", "scripts/format-imports.sh", *_parse_args()])


def run_lint():
    subprocess.run(["bash", "scripts/lint.sh", *_parse_args()])


def run_test():
    subprocess.run(["bash", "scripts/test.sh", *_parse_args()])


def run_test_cov():
    subprocess.run(["bash", "scripts/test-cov.sh", *_parse_args()])


def run_test_cov_html():
    subprocess.run(["bash", "scripts/test-cov-html.sh", *_parse_args()])
