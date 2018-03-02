from flask import Flask, render_template, request
import json
import pdb

with open("config.json") as f:
    conf = json.load(f)
    
app = Flask(__name__)

# Set "homepage" to index.html
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
