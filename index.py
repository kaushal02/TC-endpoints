from flask import Flask, jsonify, request
from flask_mongoengine import MongoEngine

from helper import debug
from models.phonepkg import Phone
from models.emailpkg import Email
from controllers.phonefetch import phoneapi
from controllers.emailfetch import emailapi

from json import dumps
from bson import json_util

app = Flask(__name__)
app.config['MONGODB_DB'] = 'TCprofiles'
app.config['MONGODB_CONNECT'] = False
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'safd4w33265ttrewf.;r[fll5;.rf4,5l.p'
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSONIFY_MIMETYPE'] = 'application/json'
db = MongoEngine(app)

def getphone(val, print_time=False):
    phoneapi(val)
    data = Phone.objects.get(pk=val)
    return jsonify(data.serialize(print_time))

def getemail(val, print_time=False):
    emailapi(val)
    data = Email.objects.get(pk=val)
    return jsonify(data.serialize(print_time))

@app.route('/get')
def get():
    if 'phone' in request.values:
        valp = request.values.get('phone')
    if 'email' in request.values:
        vale = request.values.get('email')
    if 'valp' in locals() and 'vale' in locals():
        return 'Please wait for v2.0'
    elif 'valp' in locals():
        return getphone(valp, ('ts' in request.values))
    elif 'vale' in locals():
        return getemail(vale, ('ts' in request.values))
    else:
        abort(404)

@app.route('/admin')
def getall():
    fp = False
    fe = False
    if 'email' in request.values:
        fe = True
    if 'phone' in request.values:
        fp = True

    if not (fp ^ fe):
        return app.response_class(
            response=dumps({
                'email': [c.serialize() for c in Email.objects],
                'phone': [c.serialize() for c in Phone.objects]},
                default=json_util.default, indent=4),
            status=200,
            mimetype='application/json',
        )
    elif fp:
        return app.response_class(
            response=dumps([c.serialize() for c in Phone.objects],
                           default=json_util.default, indent=4),
            status=200,
            mimetype='application/json',
        )
    elif fe:
        return app.response_class(
            response=dumps([c.serialize() for c in Email.objects],
                           default=json_util.default, indent=4),
            status=200,
            mimetype='application/json',
        )
    else:
        return "Please enter valid query"

if __name__ == '__main__':
   app.run(debug=debug)