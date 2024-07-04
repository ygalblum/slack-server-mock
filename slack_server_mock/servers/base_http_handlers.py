""" Common code for HTTP Handlers """
import json

from tornado.web import RequestHandler


def load_json_from_body(handler: RequestHandler):
    """ Load JSON from request body """
    try:
        data = json.loads(handler.request.body)
    except json.JSONDecodeError:
        handler.set_status(400)
        handler.write({"error": "Invalid JSON"})
        return None
    return data
