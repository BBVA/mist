from functools import wraps

from flask import request, abort, jsonify, Flask


def setup_custom_errors(_app: Flask):  # pragma: no cover

    @_app.errorhandler(400)
    def invalid_request(e):
        return jsonify(error=e.description), 400

    @_app.errorhandler(401)
    def request_error(e):
        return jsonify(error=e.description), 401

    @_app.errorhandler(403)
    def access_forbidden(e):
        return jsonify(error=e.description), 403

    @_app.errorhandler(404)
    def resource_not_found(e):
        return jsonify(error=e.description), 404

    @_app.errorhandler(409)
    def unauthorized(e):
        return jsonify(error=e.description), 409

    @_app.errorhandler(422)
    def unprocessable_entity(e):
        return jsonify(error=e.description), 422


def ensure_json(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            abort(400, description="JSON data required")

        return f(*args, **kwargs)

    return decorated_function
