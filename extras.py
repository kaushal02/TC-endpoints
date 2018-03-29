from math import trunc
from subprocess import Popen
from time import gmtime, strftime
from csv import reader as csvReader
from flask import send_from_directory as download
from flask import redirect, url_for, render_template

def completion(jobdir):
    with open(os.path.join(jobdir, 'raw.csv')) as f:
        todo = len(f.readlines())
    with open(os.path.join(jobdir, 'processed.csv')) as f:
        done = len(f.readlines())
    progress = int(round((done*100.)/todo))
    return min(100, progress)

@app.route('/validate', methods = ['POST'])
def login2():
    login = request.form.get('login')
    password = request.form.get('password')
    
    with open(os.path.join(homedir, 'users.csv')) as f:
        # login,password,name
        reader = csvReader(f, delimiter=',')
        for i, line in enumerate(reader):
            if (line[0]==login) and (line[1]==password):
                name = line[2]
                return redirect(url_for('jobs', login = login, landing = ""))

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
        reader = csvReader(f, delimiter=',')
        for i, line in enumerate(reader):
            if (line[0]==login):
                name = line[2]
    
    if not 'name' in locals():
        return redirect(url_for('index'))

    logindir = os.path.join(homedir, 'Data', login)
    if os.path.isdir(logindir):
        folders = os.listdir(logindir)
    else:
        folders = []
    subdirs = [folder for folder in folders if
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
                               notstarted = "")

    # Check if the fetching is complete
    try:
        os.kill(int(pid), 0)
    except OSError:
        running = False
    else:
        running = True

    progress = completion(jobdir)
    if (running==True) and (progress<90):
        return render_template('directory.html', name = name,
                               login = login, subdirs = subdirs,
                               progress = progress)
    elif progress < 90:
        return render_template('directory.html', name = name,
                               login = login, subdirs = subdirs,
                               failed = "")
    else:
        return render_template('directory.html', name = name,
                               login = login, subdirs = subdirs,
                               cursubdir = subdir)

@app.route('/files/<login>/<subdir>')
def files(login, subdir):
    return download(os.path.join(homedir, 'Data', login, subdir),
                    'processed.csv', as_attachment = True,
                    attachment_filename = '%s_data.csv' % subdir)

import sys, json, csv, subprocess, requests

if __name__ == '__main__':
    
    TaskId = str(sys.argv[1])
    # JSON file
    path_json = 'Data/Jobs/' + TaskId + '/info.json'
    with open(path_json) as infile:
        info = json.load(infile)
        TaskId = info['taskid']
        column_phone = 1
        column_email = 2

    # raw file
    file_data_raw = 'Data/Jobs/' + TaskId + '/raw.csv'
    # processed file
    file_data_processed = 'Data/Jobs/' + TaskId + '/processed.csv'

    # Final fields
    fields_phone = ['P_name', 'P_confidence', 'P_gender',
                    'P_gender_confidence', 'P_address', 'P_email',
                    'P_fb_id', 'P_fb_name', 'P_fb_imageurl']
    fields_email = ['E_dob', 'E_gender', 'E_googleid',
                    'E_name', 'E_photo', 'E_friends',
                    'E_extrainfocount']
    fields_all = fields_phone + fields_email
    final = []
    with open(file_data_raw) as infile:
        reader = csv.reader(infile, delimiter=',')
        for i, line in enumerate(reader):
            final.append({})            
            
            # Calling phone-api
            phone = line[column_phone-1]
            phoneapi = requests.get('https://truecheckr.com/api/phone-api' + 
                '?apiKey=BC9c7ZVWp6dTdMa4HCzrItFP4r7rDprLGdsWHWL6zuw' +
                '&phone_num=91' + phone).json()['status']
            if ('code' in phoneapi) and phoneapi['code'] == 0:
                # successful
                try:
                    data = phoneapi['data']['value']
                    if 'name' in data:
                        final[i]['P_name'] = data['name']
                    if 'confidence' in data:
                        final[i]['P_confidence'] = data['confidence']
                    
                    if 'gender_details' in data:
                        if len(data['gender_details'])>0:
                            tdata = data['gender_details'][0]
                            if 'gender' in tdata:
                                final[i]['P_gender'] = tdata['gender']
                            if 'score' in tdata:
                                final[i]['P_gender_confidence'] = tdata['score']
                    
                    if 'location_details' in data:
                        if len(data['location_details'])>0:
                            final[i]['P_address'] = data['location_details'][0]['city']

                    if 'social_details' in data:
                        tdata = data['social_details']
                        if 'email' in tdata[0]:
                            final[i]['P_email'] = tdata[0]['email']
                        if 'facebook_id' in tdata[1]:
                            final[i]['P_fb_id'] = tdata[1]['facebook_id']
                        if 'facebook_name' in tdata[1]:
                            final[i]['P_fb_name'] = tdata[1]['facebook_name']
                        if 'facebook_image' in tdata[1]:
                            final[i]['P_fb_imageurl'] = tdata[1]['facebook_image']
                except:
                    pass

            # Calling email-api
            email = line[column_email-1]
            emailapi = requests.get('https://www.truecheckr.com/api/searchemail-api' +
                '?email=' + email +
                '&apiKey=Ie5JtImyHR9ORznuJLCocVP5ryURpz0Qv8gt44fTf1Q').json()['status']
            if ('code' in emailapi) and emailapi['code'] == 0:
                # successful
                try:
                    data = emailapi['data']['googleapis']
                    ecdata = emailapi['data']['email_check']
                    if 'birthday' in data:
                        final[i]['E_dob'] = data['birthday']
                    if 'gender' in data:
                        final[i]['E_gender'] = data['gender']
                    elif 'gender' in ecdata:
                        final[i]['E_gender'] = ecdata['gender']
                    if 'id' in data:
                        final[i]['E_googleid'] = data['id']
                    if 'displayName' in data:
                        final[i]['E_name'] = data['displayName']
                    if 'image' in data:
                        if 'isDefault' in data['image']:
                            if not data['image']['isDefault']:
                                final[i]['E_photo'] = data['image']['url']
                    if ('isPlusUser' in data) and data['isPlusUser']:
                        if 'circledByCount' in data:
                            final[i]['E_friends'] = data['circledByCount']
                    extras = 0
                    extracol = False
                    if 'urls' in data:
                        extracol = True
                        extras += len(data['urls'])
                    if 'placesLived' in data:
                        extracol = True
                        extras += len(data['placesLived'])
                    if 'organizations' in data:
                        extracol = True
                        extras += len(data['organizations'])
                    if extracol:
                        final[i]['E_extrainfocount'] = extras
                except:
                    pass

            # Calling other email-api
            email2api = requests.get('https://api.fullcontact.com/v2/' + 
                'person.json?email=' + email, headers={'X-FullContact-APIKey':
                'CYUduQUw2hKkPTotMEDrgqRAqU2j8Svz'}).json()['status']


    # writing gathered data to a file
    with open(file_data_processed, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fields_all)
        writer.writeheader()
        writer.writerows(final)

    # sending email script invoke
    subprocess.Popen(['python', 'send.py', TaskId, '&; disown'])

import os
import json
from pytz import timezone
from random import randint
from subprocess import Popen
from datetime import datetime
from validate_email import validate_email
from flask import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate', methods = ['POST'])
def login():
    name = request.form.get('name')
    email = request.form.get('email')
    
    if len(name) == 0:
        return render_template(
            'index.html', email = email,
            error = "Please enter your name")
    
    elif len(email) == 0:
        return render_template(
            'index.html', name = name,
            error = "Please enter an email address")
    
    elif validate_email(email,verify=True) != True:
        return render_template(
            'index.html', name = name,
            error = "The email address you provided is not supported by us. \
            Please enter another email address")
    
    else:
        return render_template('upload.html', name = name, email = email)

@app.route('/submit', methods = ['POST'])
def upload():
    name = request.form.get('name')
    email = request.form.get('email')
    f = request.files['file']
    
    ### Create a new directory holding all relevant files for this transaction
    # Generate a unique TaskId
    while True:
        TaskId = str(randint(1,1E6))
        if not os.path.isdir('Data/Jobs/%s' % TaskId):
            break
    os.mkdir('Data/Jobs/' + TaskId)
    # Store uploaded file as raw.csv
    file_uploaded = 'Data/Jobs/%s/raw.csv' % TaskId
    f.save(file_uploaded)
    # Write task details in info.json
    path_json = 'Data/Jobs/%s/info.json' % TaskId
    curtime = datetime.now(timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    data = {'taskid': TaskId,
            'name': name,
            'email': email,
            'submitted': curtime,
    }
    with open(path_json, 'w') as outfile:
        json.dump(data, outfile)

    ### Run the process
    pid = Popen(['python', 'fetch.py', TaskId, '&; disown']).pid

    ### Store the job details in a master file
    with open('Data/jobs.txt', 'a') as f:
        f.write('pid=%s assigned to %s @%s\n' % (str(pid), TaskId, curtime))

    return render_template('confirm.html', id = TaskId, name = name, email = email)

if __name__ == '__main__':
   app.run(debug = True)

from flask import Flask, flash, redirect, render_template, request, url_for
app = Flask(__name__)
app.secret_key = 'random string'

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
   error = None
   
   if request.method == 'POST':
      if request.form['username'] != 'admin' or \
      request.form['password'] != 'admin':
         error = 'Invalid username or password. Please try again!'
      else:
         return redirect(url_for('index'))
            
   return render_template('login.html', error = error)

if __name__ == "__main__":
   app.run(debug = True)

# import SimpleHTTPServer
# import SocketServer

# PORT = 8001
# Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
# httpd = SocketServer.TCPServer(('', PORT), Handler)
# print 'serving at port', PORT
# httpd.serve_forever()
################################################################################

# from bottle import route, run, template

# @route('/hello/<name>')
# def index(name):
#     return template('<b>Hello {{name}}</b>!', name=name)

# run(host='localhost', port=8001)
################################################################################

# import os
# from flask import Flask, request, redirect, url_for
# from werkzeug.utils import secure_filename

# UPLOAD_FOLDER = '.'
# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# app.run()

# @app.route("/echo")
# def echo(): 
#     return "You said: " + request.args.get('text', '')
################################################################################

import os, sys, subprocess, json, random
from datetime import datetime
from pytz import timezone

# Generate a unique TaskId
while True:
    TaskId = str(random.randint(1,1E6))
    if not os.path.isdir('Data/Jobs/' + TaskId):
        break
# Create a new directory holding all relevant files for this user
os.mkdir('Data/Jobs/' + TaskId)
# Uploaded file
file_up
loaded = 'Data/Jobs/' + TaskId + '/raw.csv'
# Store it in Data/Jobs/TaskId/
os.system('cp ' + str(sys.argv[1]) + ' ' + file_uploaded)
# JSON file
path_json = 'Data/Jobs/' + TaskId + '/info.json'

# Write task details in info.json
user_name = str(sys.argv[2])
user_email = str(sys.argv[3])
current_time = datetime.now(timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
column_phone = str(sys.argv[4])
column_email = str(sys.argv[5])
data = {'taskid': TaskId,
        'name': user_name,
        'email': user_email,
        'submitted': current_time,
        'column': {
            'phone': column_phone,
            'email': column_email
        }}
with open(path_json, 'w') as outfile:
    json.dump(data, outfile)

pid = subprocess.Popen(['python', 'fetch.py', TaskId, '&; disown']).pid

with open('Data/jobs.txt', 'a') as outfile:
    outfile.write('pid=' + str(pid) + ' assigned to ' + TaskId + ' @' + current_time + '\n')

