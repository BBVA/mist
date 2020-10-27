from flask import Flask, render_template


def setup_editor(_app: Flask):

    @_app.route("/editor", methods=["GET"])
    def start_editor():
        return render_template("index.html")
