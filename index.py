import os
from myfunc import debug
from myphone import phoneapi
from myemail import emailapi
from flask_pymongo import PyMongo
from flask import Flask, request, jsonify

from json import dumps
from bson import json_util

app = Flask(__name__)
app.secret_key = 'safd4w33265ttrewf.;r[fll5;.rf4,5l.p'
app.config['MONGO_DBNAME'] = 'TCdbs'
mongo = PyMongo(app)
homedir = os.path.dirname(os.path.abspath(__file__))

def getphone(val):
    valdata = mongo.db.phonedb.find_one({'value': val}, {'_id':0})
    if not valdata:
        z = phoneapi(val)
        if z:
            valdata = mongo.db.phonedb.find_one(mongo.db.phonedb.insert_one(
                        z).inserted_id, {'_id':0})
    return jsonify(valdata)

def getemail(val):
    valdata = mongo.db.emaildb.find_one({'value': val}, {'_id':0})
    if not valdata:
        z = emailapi(val)
        if z:
            valdata = mongo.db.emaildb.find_one(mongo.db.emaildb.insert_one(
                        z).inserted_id, {'_id':0})
    return jsonify(valdata)

@app.route('/get')
def get():
    if 'phone' in request.values:
        valp = request.values.get('phone')
    if 'email' in request.values:
        vale = request.values.get('email')
    if 'valp' in locals() and 'vale' in locals():
        return 'Need more coding for this bro!'
    elif 'valp' in locals():
        return getphone(valp)
    elif 'vale' in locals():
        return getemail(vale)
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
                'email': [c for c in mongo.db.emaildb.find({}, {'_id':0})],
                'phone': [c for c in mongo.db.phonedb.find({}, {'_id':0})]},
                default=json_util.default, indent=4),
            status=200,
            mimetype='application/json'
        )
    elif fp:
        return app.response_class(
            response=dumps([c for c in mongo.db.phonedb.find({}, {'_id':0})],
                           default=json_util.default, indent=4),
            status=200,
            mimetype='application/json'
        )
    elif fe:
        return app.response_class(
            response=dumps([c for c in mongo.db.emaildb.find({}, {'_id':0})],
                           default=json_util.default, indent=4),
            status=200,
            mimetype='application/json'
        )
    else:
        return "Please enter valid query"

if __name__ == '__main__':
   app.run(debug=debug)