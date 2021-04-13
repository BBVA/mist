from flask import Flask, render_template
import json

def setup_editor(_app: Flask):

    @_app.route("/editor", methods=["GET"])
    def start_editor():
        return render_template("index.html",cheatsheet=_app.cheatsheet)

    @_app.route("/mode-mist.js", methods=["GET"])
    def mode_mist():
        return render_template("mode-mist.js",commands='|'.join(_app.commands))
