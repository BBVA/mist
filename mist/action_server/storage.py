import abc
import base64
import urllib.parse as ps

from redis import Redis as RedisServer

from flask import g, current_app
from werkzeug.local import LocalProxy


class _Storage(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_job(self, job_id: str):
        pass

    @abc.abstractmethod
    def store_job_result(self, job_id: str, console: str, database_path: str):
        pass

    @abc.abstractmethod
    def job_status(self, job_id: str) -> str:
        pass

    @abc.abstractmethod
    def set_job_running(self, job_id: str):
        pass

    @abc.abstractmethod
    def get_job_console(self, job_id: str) -> str or None:
        pass

    @abc.abstractmethod
    def get_job_database(self, job_id: str) -> bytes or None:
        pass

    def load_database_from_path(self, path: str) -> str:
        """Read sqlite database and return it as binary encoded in base 64"""
        with open(path, "rb") as db_path:
            content = db_path.read()

        return base64.encodebytes(content).decode()

    def dump_database_from_bytes(self, content: bytes) -> bytes:
        return base64.decodebytes(content)



class Memory(_Storage):

    def __init__(self):
        self._console = {}
        self._job_status = {}
        self._databases = {}

    def create_job(self, job_id: str):
        self._job_status[job_id] = "created"
        self._console[job_id] = None

    def job_status(self, job_id: str) -> str:
        try:
            return self._job_status[job_id]
        except KeyError:
            return None

    def set_job_running(self, job_id: str):
        self._job_status[job_id] = "running"

    def store_job_result(self, job_id: str, console: str, database_path: str):
        self._job_status[job_id] = "finished"
        self._console[job_id] = console

        if database_path:
            self._databases[job_id] = self.load_database_from_path(
                database_path
            )

    def get_job_console(self, job_id: str) -> str or None:
        try:
            return self._console[job_id]
        except KeyError:
            return None

    def get_job_database(self, job_id: str) -> bytes or None:
        try:
            return self._databases[job_id]
        except KeyError:
            return None


class Redis(_Storage):

    def __init__(self, connection_string: str):
        parsed = ps.urlparse(connection_string)

        if parsed.scheme != "redis":
            raise ValueError(
                "Invalid Redis connection string. Correct format is: "
                "redis://user:password@host:port/db"
            )

        db = parsed.path
        if db and db.startswith("/"):
            db = db[1:]

        self._connection = RedisServer(
            host=parsed.hostname,
            port=parsed.port,
            db=db,
            username=parsed.username,
            password=parsed.password
        )

    @staticmethod
    def status_prefix(job_id: str):
        return f"mist:server:job-status:{job_id}"

    @staticmethod
    def result_prefix(job_id: str):
        return f"mist:server:job-console:{job_id}"

    @staticmethod
    def result_database(job_id: str):
        return f"mist:server:job-database:{job_id}"

    def create_job(self, job_id: str):
        self._connection.set(
            Redis.status_prefix(job_id),
            "created"
        )

    def job_status(self, job_id: str) -> str:
        return self._connection.get(
            Redis.status_prefix(job_id)
        ).decode("UTF-8")

    def set_job_running(self, job_id: str):
        self._connection.set(
            Redis.status_prefix(job_id),
            "running"
        )

    def store_job_result(self, job_id: str, console: str, database_path: str):
        self._connection.set(
            Redis.status_prefix(job_id),
            "finished"
        )

        self._connection.set(
            Redis.result_prefix(job_id),
            console
        )

        if database_path:
            if db_content := self.load_database_from_path(database_path):
                self._connection.set(
                    Redis.result_database(job_id),
                    db_content
                )

    def get_job_console(self, job_id: str) -> str or None:
        if k := self._connection.get(Redis.result_prefix(job_id)):
            return k.decode()
        else:
            return None

    def get_job_database(self, job_id: str) -> str or None:
        if k := self._connection.get(Redis.result_database(job_id)):
            return k.decode()
        else:
            return None


def _setup_storage() -> _Storage:
    if 'jobs' not in g:
        if current_app.config["REDIS_CONNECTION_STRING"] is None:
            storage = Memory()
        else:
            storage = Redis(current_app.config["REDIS_CONNECTION_STRING"])

        g.jobs = storage

    return g.jobs

current_jobs: _Storage = LocalProxy(_setup_storage)
