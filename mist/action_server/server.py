import argparse
import os.path as op
import tempfile

from flask import Flask, jsonify, request, abort
from flask_executor import Executor
from flask_sse import sse

from .editor import setup_editor
from .helpers import setup_custom_errors, ensure_json
from .realtime import setup_realtime
from .storage import Redis, current_jobs
from ..action_run import execute_from_text
from ..guuid import guuid

import asyncio

here = op.dirname(__file__)

app = Flask("mist",
            root_path=here,
            static_folder=op.join(here, "assets"),
            template_folder=op.join(here, "templates"))
executor = Executor()

setup_custom_errors(app)

def bg_run(redis_con: str, job_id: str, mist_content: str, parameters: dict):
    _tmp_app = Flask("mist_tmp")
    _tmp_app.config["REDIS_URL"] = redis_con

    def realtime_callback(msg: str):
        with _tmp_app.app_context():
            sse.publish({"message": msg}, channel=job_id)

    storage = Redis(redis_con)

    #
    # Change status to run
    #
    with tempfile.NamedTemporaryFile(prefix="mist-db-server") as db:

        storage.set_job_running(job_id)
        try:
            results = asyncio.run(execute_from_text(                
                text=mist_content,
                fn_params=parameters,
                realtime_fn=realtime_callback,
                database_path=db.name
            )) 
            storage.store_job_result(
                job_id,
                results,
                db.name
            )
        except Exception as e:
            storage.store_job_result(job_id, str(e), None)


@app.route("/run/<job_id>/status", methods=["GET"])
def get_status(job_id):
    if status := current_jobs.job_status(job_id):
        return jsonify({"status": status})
    else:
        return jsonify({"error": "job doesn't exits"})


@app.route("/run/<job_id>", methods=["GET"])
def get_results(job_id):
    if not (status := current_jobs.job_status(job_id)):
        return jsonify({"error": "job doesn't exits"})

    if status != "finished":
        return jsonify({"message": "job already running"})
    else:
        return jsonify({"message": current_jobs.get_job_console(job_id)})


@app.route("/run/<job_id>/db", methods=["GET"])
def get_db_results(job_id):
    if not (status := current_jobs.job_status(job_id)):
        return jsonify({"error": "job doesn't exits"})

    if status != "finished":
        return jsonify({"message": "job already running"})
    else:
        return jsonify({"message": current_jobs.get_job_database(job_id)})


@app.route("/run", methods=["POST"])
@ensure_json
def run_command():
    content = request.json.get("content", None)
    parameters = request.json.get("parameters", None)

    if not content:
        return jsonify({"jobId": ""})

    if parameters:
        if type(parameters) is not dict:
            abort(400,
                  description="Invalid request. Parameters must a valid "
                              "JSON")

    #
    # Create job ID
    #
    job_id = guuid()
    current_jobs.create_job(job_id)

    executor.submit(
        bg_run,
        app.config["REDIS_CONNECTION_STRING"],
        job_id,
        content, parameters
    )

    return jsonify({"jobId": job_id})


def run_server(parsed_args: argparse.Namespace):
    listen_port = parsed_args.port
    listen_addr = parsed_args.listen_addr
    enable_editor = parsed_args.enable_editor
    concurrency = parsed_args.concurrency
    redis_connection_string = parsed_args.redis_server

    if enable_editor:
        setup_editor(app)

        print(f" * Starting editor at: http://localhost:{listen_port}/editor")
        print(f"   BE CAREFUL: YOU MUST USE 'localhost' NOT '127.0.0.1'")

    #
    # Some config
    #

    setup_realtime(app, parsed_args)

    app.config["REDIS_CONNECTION_STRING"] = redis_connection_string
    app.config["EXECUTOR_TYPE"] = "process"
    app.config["EXECUTOR_MAX_WORKERS"] = concurrency
    app.config['EXECUTOR_PROPAGATE_EXCEPTIONS'] = True

    #TODO: fill with commands from catalog and builtin functions
    app.commands, app.cheatsheet = [], []
    executor.init_app(app)

    app.run(host=listen_addr, port=listen_port, debug=False)
