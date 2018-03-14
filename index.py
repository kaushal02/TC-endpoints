import os
import csv
from math import trunc
from subprocess import Popen
from time import gmtime, strftime
from flask import *

app = Flask(__name__)
homedir = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate', methods = ['POST'])
def login():
    login = request.form.get('login')
    password = request.form.get('password')
    
    with open(os.path.join(homedir, 'users.csv')) as f:
        # login,password,name
        reader = csv.reader(f, delimiter=',')
        for i, line in enumerate(reader):
            if (line[0]==login) and (line[1]==password):
                name = line[2]
                return render_template('upload.html', name = name, login = login)

    return render_template('index.html', error = 1)

@app.route('/submit', methods = ['POST'])
def upload():
    login = request.form.get('login')
    
    # Get paths
    logindir = os.path.join(homedir, 'Data', login)
    ### if not os.path.isdir(logindir):
    ###     os.mkdir(logindir)
    # Use Time as unique hash
    curtime = strftime('%d%b%y_%Hh%Mm%Ss', gmtime())
    jobdir = os.path.join(logindir, curtime)
    os.makedirs(jobdir)
    # Store uploaded file as raw.csv
    request.files['file'].save(os.path.join(jobdir, 'raw.csv'))
    
    # Start the process
    pid = Popen(['python', os.path.join(homedir, 'fetch.py'), jobdir, 
                '&; disown']).pid
    # Store the job details in corresponding master file
    with open(os.path.join(logindir, 'jobs.csv'), 'a') as f:
        f.write('%s,%s\n' % (str(pid), curtime))

    return redirect(url_for('jobs', login = login, pid = pid, subdir = curtime))

@app.route('/jobs/<login>')
def jobs(login):
    pid = request.args.get('pid')
    subdir = request.args.get('subdir')
    logindir = os.path.join(homedir, 'Data', login)
    jobdir = os.path.join(logindir, subdir)
    name = "Kaushal"

    # Check if the fetching has started
    if not os.path.exists(os.path.join(jobdir, 'processed.csv')):
        return render_template('directory.html', notstarted = 1, name = name)

    # Check if the fetching is complete
    try:
        os.kill(int(pid), 0)
    except OSError:
        running = True
    else:
        running = False

    # Progress
    with open(os.path.join(jobdir, 'raw.csv')) as f:
        todo = len(f.readlines())
    with open(os.path.join(jobdir, 'processed.csv')) as f:
        done = len(f.readlines())
    progress = trunc((done*100)/todo)
    if progress > 100:
        progress = 100

    if running==True:
        return render_template('directory.html', progress = progress, name = name)
    elif progress < 100:
        return render_template('directory.html', failed = 1, name = name)
    else:
        return render_template('directory.html', done = 1, name = name)
    
if __name__ == '__main__':
   app.run(debug=True)
