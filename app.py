from flask_caching import Cache
from flask import Flask, render_template, request, make_response
import json
import psycopg2
from psycopg2 import sql
import webbrowser
import StringIO
from unicodecsv import writer as csvwriter
import sys
import traceback
import pdb
    
#Initialize app, checking if frozen in exe
if getattr(sys, 'frozen', False):                                                                                                                                     
    template_folder = os.path.abspath(os.path.join(sys.executable, '..','templates'))                                                                                                  
    static_folder = os.path.abspath(os.path.join(sys.executable, '..','static'))
    config_folder = os.path.abspath(os.path.join(sys.executable, '..','config','config.json'))
    with open(config_folder) as f:
        conf = json.load(f)
    app = Flask(__name__, template_folder = template_folder,static_folder = static_folder)
else:
    with open('config/config.json') as f:
        conf = json.load(f)
    app = Flask(__name__)
#Initialize cache
cache = Cache(app,config={'CACHE_TYPE':'simple'})

# Set "homepage" to index.html
@app.route('/')
@cache.cached(timeout=3600)
def index():
    #Try to connect
    try:
        conn = psycopg2.connect("dbname='{}' user='{}' host='{}' port='{}' password='{}'".format(conf["dbname"],conf["user"],conf["host"],conf["port"],conf["password"],))
        cur = conn.cursor()
        #Query all table names
        cur.execute("""SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema') ORDER BY table_schema, table_name""")
        table_names = cur.fetchall()
        #Flatten array of tuples
        conn.close()
        return render_template('index.html',table_names=table_names)
    except:
        return render_template('index.html',table_names=[])
    
#Route for table displays
@app.route('/table/<table_name>')
@cache.cached(timeout=3600)
def table(table_name):
    #Try to connect
    try:
        conn = psycopg2.connect("dbname='{}' user='{}' host='{}' port='{}' password='{}'".format(conf["dbname"],conf["user"],conf["host"],conf["port"],conf["password"],))
        cur = conn.cursor()
        #Verify table exists
        cmd = "SELECT 1 FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema') and table_name=%s LIMIT 1"
        cur.execute(cmd,(table_name,))
        table_exists = cur.fetchall()
        if len(table_exists) < 1:
            #Table does not exist
            conn.close()
            return render_template('error.html',error="Table does not exist.")
        else:
            #Select all from the given table_name
            cur.execute(
                sql.SQL('SELECT * FROM {}')
                    .format(sql.Identifier(table_name))
            )
            col_names = [desc[0] for desc in cur.description]
            table_rows = cur.fetchall()
            conn.close()
            table_rows = [[unicode(cell,'utf-8') if isinstance(cell,basestring) else cell for cell in row] for row in table_rows]
            return render_template('table.html',table_name=table_name,col_names=col_names,table_rows=table_rows)
    except:
        return render_template('error.html',error=traceback.format_exc())
    
#Route for CSVs
@app.route('/csv/<table_name>')
@cache.cached(timeout=3600)
def csv(table_name):
    #Try to connect
    try:
        conn = psycopg2.connect("dbname='{}' user='{}' host='{}' port='{}' password='{}'".format(conf["dbname"],conf["user"],conf["host"],conf["port"],conf["password"],))
        cur = conn.cursor()
        #Verify table exists
        cmd = "SELECT 1 FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema') and table_name=%s LIMIT 1"
        cur.execute(cmd,(table_name,))
        table_exists = cur.fetchall()
        if len(table_exists) < 1:
            #Table does not exist
            conn.close()
            return render_template('error.html',error="Table does not exist.")
        else:
            #Select all from the given table_name
            cur.execute(
                sql.SQL('SELECT * FROM {}')
                    .format(sql.Identifier(table_name))
            )
            col_names = [desc[0] for desc in cur.description]
            table_rows = cur.fetchall()
            conn.close()
            table_rows = [[unicode(cell,'utf-8') if isinstance(cell,basestring) else cell for cell in row] for row in table_rows]
            si = StringIO.StringIO()
            cw = csvwriter(si,encoding='latin-1')
            cw.writerow(col_names)
            cw.writerows(table_rows)
            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = "attachment; filename={}.csv".format(table_name)
            output.headers["Content-type"] = "text/csv"
            return output
    except:
        return render_template('error.html',error=traceback.format_exc())
    

if __name__ == '__main__':
    webbrowser.open("http://localhost:5000")
    app.run(threaded=True)
