from flask import Flask, render_template
from ..action_catalog import Catalog
import json

def setup_editor(_app: Flask):

    @_app.route("/editor", methods=["GET"])
    def start_editor():
        cheatsheet = Catalog.get_cheatsheet()
        return render_template("index.html",cheatsheet=cheatsheet)

    @_app.route("/mode-mist.js", methods=["GET"])
    def mode_mist():
        commands = Catalog.find_all_command_names()
        return render_template("mode-mist.js",commands='|'.join(commands))
