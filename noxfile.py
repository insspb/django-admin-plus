"""Nox tool configuration file.

Nox is Tox tool replacement.
"""
import nox

nox.options.keywords = "not docs"


def base_install(session):
    """Creates basic environment setup for tests and linting."""
    session.install("-r", "requirements.txt")
    session.install("-e", ".")
    return session


@nox.session(python=["3.7", "3.8", "3.9", "3.10"])
@nox.parametrize(
    "django",
    [
        "Django>=3.0,<3.1",
        "Django>=3.1,<3.2",
        "Django>=3.2,<4.0",
        "Django>=4.0a1,<5.0",
        "https://github.com/django/django/archive/main.tar.gz",
    ],
    ids=["3.0", "3.1", "3.2", "4.0", "latest"],
)
def tests(session, django):
    """Run test suite with pytest."""
    # Skip tests for unsupported matrix values.
    if session.python == "3.7" and django in (
        "Django>=4.0a1,<5.0",
        "https://github.com/django/django/archive/main.tar.gz",
    ):
        session.skip("Unsupported Django version and python version combination.")

    session.install(django)
    session = base_install(session)
    session.run("pytest", "--cov-report=html", "--cov-report=xml")


@nox.session(python="3.8")
def linting(session):
    """Launch linting locally."""
    session = base_install(session)
    session.run("pre-commit", "run", "-a")


@nox.session(python="3.8")
def docs(session):
    """Build the documentation."""
    session.run("rm", "-rf", "docs/build", external=True)
    session.install("-r", "docs/requirements.txt")
    session.install(".")
    session.cd("docs")
    sphinx_args = ["-b", "html", "-W", "source", "build/html"]

    if not session.interactive:
        sphinx_cmd = "sphinx-build"
    else:
        sphinx_cmd = "sphinx-autobuild"
        sphinx_args.extend(["--open-browser", "--port", "9812"])

    session.run(sphinx_cmd, *sphinx_args)
