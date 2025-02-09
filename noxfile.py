import nox
import os

# Force nox to use UV and set Python version preference
nox.options.default_venv_backend = "uv"
os.environ["UV_PYTHON_VERSION"] = "3.11"


def install_with_uv(session: nox.Session, *args, **kwargs):
    """Install dependencies using UV instead of pip."""
    session.run("uv", "pip", "install", *args, env={"UV_PYTHON_VERSION": session.python}, **kwargs)


@nox.session(python=["3.8", "3.9", "3.10", "3.11"], venv_backend="uv")
def tests(session):
    """Run tests with pytest."""
    install_with_uv(session, ".[test]")
    install_with_uv(session, "pytest")
    session.run("pytest")


@nox.session(venv_backend="uv")
def lint(session):
    """Run code linting with ruff."""
    install_with_uv(session, "ruff")
    session.run("ruff", "check", ".")


@nox.session(venv_backend="uv")
def format(session):
    """Format code with ruff."""
    install_with_uv(session, "ruff")
    session.run("ruff", "format", ".")


@nox.session(venv_backend="uv")
def typecheck(session):
    """Run type checking with mypy."""
    install_with_uv(session, "mypy")
    install_with_uv(session, ".")
    session.run("mypy", "email2md")


@nox.session(venv_backend="uv")
def coverage(session):
    """Run tests with coverage reporting."""
    install_with_uv(session, "coverage[toml]", "pytest", "pytest-cov")
    install_with_uv(session, ".")
    session.run("pytest", "--cov")


@nox.session(venv_backend="uv")
def build(session):
    """Build package distributions."""
    install_with_uv(session, "build")
    session.run("python", "-m", "build")
