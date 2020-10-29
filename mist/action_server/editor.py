from flask import Flask, render_template

from mist.action_catalog import Catalog

def setup_editor(_app: Flask):

    @_app.route("/editor", methods=["GET"])
    def start_editor():
        return render_template("index.html")

    @_app.route("/mode-mist.js", methods=["GET"])
    def mode_mist():
        commands = Catalog.find_all_command_names()
        return render_template("mode-mist.js",commands='|'.join(commands))
