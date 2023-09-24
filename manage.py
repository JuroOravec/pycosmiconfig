import subprocess


def run_format():
    subprocess.run(["bash", "scripts/format.sh"])


def run_format_imports():
    subprocess.run(["bash", "scripts/format-imports.sh"])


def run_lint():
    subprocess.run(["bash", "scripts/lint.sh"])


def run_test():
    subprocess.run(["bash", "scripts/test.sh"])


def run_test_cov():
    subprocess.run(["bash", "scripts/test-cov.sh"])


def run_test_cov_html():
    subprocess.run(["bash", "scripts/test-cov-html.sh"])
