from flask import Flask, render_template, flash, request
from flask_script import Manager
from flask_bootstrap import Bootstrap
import requests
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = 's0m3s3cre+'

manager = Manager(app)
bootstrap = Bootstrap(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/inside')
def inside():
    token=request.args['token']
    r = requests.get('https://ivle.nus.edu.sg/api/Lapi.svc/Profile_View?APIKey={APIKey}&AuthToken={AuthToken}'.format(APIKey="UY5RaT4yK3lgWflM47CJo", AuthToken=token))
    name = r.json()['Results'][0]['Name'].title()
    return render_template('inside.html', token=token, name=name)

# Error Handling
# @app.errorhandler(404)
# def page_not_found(e):
#   return render_template('404.html'), 404

# @app.errorhandler(500)
# def internal_server_error(e):
#   return render_template('500.html'), 500

if __name__ == '__main__':
    manager.run()