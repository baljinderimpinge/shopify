from flask import render_template
from flask_cors import CORS, cross_origin
from app import app


@app.route('/install')
@cross_origin()
def install():
    return render_template('install.html')
