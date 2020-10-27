import abc
import argparse
import pickle
import urllib.parse as ps

from redis import Redis as RedisServer

from flask import Flask


class _Storage(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_job(self, job_id: str):
        pass

    @abc.abstractmethod
    def store_job_result(self, job_id: str, data: str):
        pass

    @abc.abstractmethod
    def job_status(self, job_id: str) -> str:
        pass

    @abc.abstractmethod
    def set_job_running(self, job_id: str):
        pass

    @abc.abstractmethod
    def get_job_data(self, job_id: str):
        pass


class Memory(_Storage):

    def __init__(self, config: argparse.Namespace):
        self._data = {}
        self._job_status = {}

    def create_job(self, job_id: str):
        self._job_status[job_id] = "created"
        self._data[job_id] = None

    def job_status(self, job_id: str) -> str:
        try:
            return self._job_status[job_id]
        except KeyError:
            return None

    def set_job_running(self, job_id: str):
        self._job_status[job_id] = "running"

    def store_job_result(self, job_id: str, data: str):
        self._job_status[job_id] = "finished"
        self._data[job_id] = data

    def get_job_data(self, job_id: str):
        return self._data[job_id]


class Redis(_Storage):

    def __init__(self, config: argparse.Namespace):
        parsed = ps.urlparse(config.redis_server)

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
        return f"mist:server:job-results:{job_id}"

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

    def store_job_result(self, job_id: str, data: str):
        self._connection.set(
            Redis.status_prefix(job_id),
            "finished"
        )

        self._connection.set(
            Redis.result_prefix(job_id),
            pickle.dumps(
                data,
                protocol=pickle.HIGHEST_PROTOCOL
            )
        )

    def get_job_data(self, job_id: str):
        if k := self._connection.get(Redis.result_prefix(job_id)):
            return pickle.loads(k)
        else:
            return None


def set_storage(_app: Flask, parsed: argparse.Namespace):

    _app.config["EXECUTOR_MAX_WORKERS"] = parsed.concurrency

    if parsed.redis_server:
        _app.jobs = Redis(parsed)
    else:
        _app.jobs = Memory(parsed)
