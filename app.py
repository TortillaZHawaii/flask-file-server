from flask import Flask, request, redirect, make_response, render_template, send_file, Response
from flask.views import MethodView
import os

app = Flask(__name__)
root = os.path.normpath("/var/server")
login = 'admin'
password = 'admin'


@app.context_processor
def path_processor():
    def join_path(path, filename):
        return os.path.join(path, filename)
    return dict(join_path=join_path)


def get_type(path):
    if os.path.isdir(path):
        return 'dir'
    else:
        return 'file'


class PathView(MethodView):
    def get(self, p=''):
        path = os.path.join(root, p)

        if os.path.isdir(path):
            contents = []
            for filename in os.listdir(path):
                filepath = os.path.join(path, filename)
                if os.path.islink(filepath):
                    continue

                info = {'name': filename, 'type': get_type(filepath)}

                contents.append(info)

            page = render_template('index.html', path=p, contents=contents)
            return make_response(page, 200)

        elif os.path.isfile(path):
            return send_file(path)

        elif os.path.islink(path):
            return make_response("Bad request: Symlinks won't be followed", 400)

        return make_response('Not found', 404)

    def post(self, p=''):
        path = os.path.join(root, p)
        
        if request.form['username'] != login or request.form['password'] != password:
            return make_response('Wrong username or password', 403)

        if os.path.isdir(path):
            files = request.files.getlist('files[]')
            for file in files:
                try:
                    file.save(os.path.join(path, file.filename))
                except Exception as e:
                    return make_response('Failure', 400)
                else:
                    return make_response(redirect(p))

        return make_response('Bad request', 400)


path_view = PathView.as_view('path_view')
app.add_url_rule('/', view_func=path_view)
app.add_url_rule('/<path:p>', view_func=path_view)


if __name__ == '__main__':
    app.run()
