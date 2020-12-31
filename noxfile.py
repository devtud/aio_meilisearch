import nox
import nox_poetry.patch  # noqa
from nox.sessions import Session


@nox.session(python=["3.8", "3.9"])
def tests(session: Session):
    session.run("poetry", "lock")
    session.install(".")
    session.install("docker")
    session.run("python", "-m", "unittest")
