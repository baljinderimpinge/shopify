from flask import request, jsonify
from flask_cors import CORS, cross_origin
from app import app


@app.route('/cart')
@cross_origin()
def cart():
    print(request.args)

    return jsonify(request.args)