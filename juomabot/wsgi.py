import traceback

from flask import Flask, Response, request

from juomabot.command import run_command
from juomabot.excs import Problem


def get_text_response(text):
    return Response(str(text).encode('utf-8'), content_type='text/plain; charset=UTF-8')


application = app = Flask(__name__)


@app.route('/slack', methods=['GET', 'POST'])
def handle_slash_command():
    data = {}
    data.update(request.form.items())
    data.update(request.args.items())
    try:
        resp = run_command(sender=data['user_name'], text=data['text'])
        return get_text_response(resp or 'no response')
    except Problem as prb:
        return get_text_response(prb.as_slack())
    except:  # pragma: no cover
        return get_text_response('An error occurred while processing this command: %s' % traceback.format_exc())
