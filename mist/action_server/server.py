import argparse
import tempfile
import os.path as op

from flask_sse import sse
from flask_executor import Executor
from flask import Flask, request, jsonify, abort, current_app

from mist.action_run import execute_from_text

from ..guuid import guuid
from .storage import setup_storage
from .editor import setup_editor
from .helpers import ensure_json, setup_custom_errors
from .realtime import setup_realtime

from ..action_catalog import Catalog

here = op.dirname(__file__)

app = Flask("mist",
            root_path=here,
            static_folder=op.join(here, "assets"),
            template_folder=op.join(here, "templates"))
executor = Executor()

setup_custom_errors(app)

def bg_run(job_id: str, mist_content: str, parameters: dict):

    def realtime_callback(msg: str):
        sse.publish({"message": msg}, channel=job_id)

    #
    # Change status to run
    #
    with tempfile.NamedTemporaryFile(prefix="mist-db-server") as db:

        with current_app.app_context():
            jobs = current_app.jobs
            jobs.set_job_running(job_id)

            try:
                results = execute_from_text(
                    text=mist_content,
                    fn_params=parameters,
                    realtime_fn=realtime_callback,
                    database_path=db.name
                )

                jobs.store_job_result(
                    job_id,
                    results,
                    db.name
                )
            except Exception as e:
                jobs.store_job_result(job_id, {"error": str(e)})


@app.route("/run/<job_id>/status", methods=["GET"])
def get_status(job_id):
    if status := app.jobs.job_status(job_id):
        return jsonify({"status": status})
    else:
        return jsonify({"error": "job doesn't exits"})

@app.route("/run/<job_id>", methods=["GET"])
def get_results(job_id):

    if not (status := app.jobs.job_status(job_id)):
        return jsonify({"error": "job doesn't exits"})

    if status != "finished":
        return jsonify({"message": "job already running"})
    else:
        return jsonify({"message": app.jobs.get_job_console(job_id)})

@app.route("/run/<job_id>/db", methods=["GET"])
def get_db_results(job_id):

    if not (status := app.jobs.job_status(job_id)):
        return jsonify({"error": "job doesn't exits"})

    if status != "finished":
        return jsonify({"message": "job already running"})
    else:
        return jsonify({"message": app.jobs.get_job_database(job_id)})

@app.route("/run", methods=["POST"])
@ensure_json
def run_command():
    content = request.json.get("content", None)
    parameters = request.json.get("parameters", None)

    if not content:
        return jsonify({"jobId": ""})

    if parameters:
        if type(parameters) is not dict:
            abort(400, description="Invalid request. Parameters must a valid JSON")

    #
    # Create job ID
    #
    job_id = guuid()
    app.jobs.create_job(job_id)

    executor.submit(bg_run, job_id, content, parameters)

    return jsonify({"jobId": job_id})

def run_server(parsed_args: argparse.Namespace):
    listen_port = parsed_args.port
    listen_addr = parsed_args.listen_addr
    enable_editor = parsed_args.enable_editor

    if enable_editor:
        setup_editor(app)

        print(f" * Starting editor at: http://localhost:{listen_port}/editor")
        print(f"   BE CAREFUL: YOU MUST USE 'localhost' NOT '127.0.0.1'")

    #
    # Some config
    #
    setup_storage(app, parsed_args)
    setup_realtime(app, parsed_args)

    executor.init_app(app)

    app.commands = Catalog.find_all_command_names()
    app.cheatsheet = Catalog.get_cheatsheet()

    app.run(host=listen_addr, port=listen_port, debug=False)
