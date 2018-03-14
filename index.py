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
                return redirect(url_for('jobs', login = login, landing = True))

    return render_template('index.html', error = 1)

@app.route('/upload/<login>')
def upload(login):
    return render_template('upload.html', login = login)

@app.route('/submit', methods = ['POST'])
def submit():
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
    with open(os.path.join(homedir, 'users.csv')) as f:
        #login,password,name
        reader = csv.reader(f, delimiter=',')
        for i, line in enumerate(reader):
            if (line[0]==login):
                name = line[2]
    
    if not 'name' in locals():
        return redirect(url_for('index'))

    logindir = os.path.join(homedir, 'Data', login)
    subdirs = [folder for folder in os.listdir(logindir) if
               os.path.isdir(os.path.join(logindir, folder))]
    if 'landing' in request.args:
        return render_template('directory.html', name = name,
                               login = login, subdirs = subdirs)

    pid = request.args.get('pid')
    subdir = request.args.get('subdir')
    jobdir = os.path.join(logindir, subdir)

    # Check if the fetching has started
    if not os.path.exists(os.path.join(jobdir, 'processed.csv')):
        return render_template('directory.html', name = name,
                               login = login, subdirs = subdirs,
                               notstarted = True)

    # Check if the fetching is complete
    try:
        os.kill(int(pid), 0)
    except OSError:
        running = False
    else:
        running = True

    # Progress
    with open(os.path.join(jobdir, 'raw.csv')) as f:
        todo = len(f.readlines())
    with open(os.path.join(jobdir, 'processed.csv')) as f:
        done = len(f.readlines())
    progress = int(trunc((done*100.)/todo))
    if progress > 100:
        progress = 100

    if running==True and progress < 90:
        return render_template('directory.html', name = name,
                               login = login, subdirs = subdirs,
                               progress = progress)
    elif progress < 90:
        return render_template('directory.html', name = name,
                               login = login, subdirs = subdirs,
                               failed = True)
    else:
        return render_template('directory.html', name = name,
                               login = login, subdirs = subdirs,
                               cursubdir = subdir)

@app.route('/files/<login>/<subdir>')
def files(login, subdir):
    return send_from_directory(os.path.join(homedir, 'Data', login, subdir),
                               'processed.csv')

if __name__ == '__main__':
   app.run(debug=1)