with open(os.path.join(homedir, 'users.csv')) as f:
    reader = reader(f, delimiter=',')
    for i, line in enumerate(reader):
        if (line[0]==login) and (line[1]==password):

curtime = strftime('%d%b%y_%Hh%Mm%Ss', gmtime())
os.makedirs(jobdir)
# Store uploaded file as raw.csv
request.files['file'].save(os.path.join(jobdir, 'raw.csv'))

# Start the process
pid = Popen(['python', os.path.join(homedir, 'fetch.py'), jobdir, 
            '&; disown']).pid
# Store the job details in corresponding master file
with open(os.path.join(logindir, 'jobs.csv'), 'a') as f:
    f.write('%s,%s\n' % (str(pid), curtime))

return send_from_directory(os.path.join(homedir, 'Data', login, subdir),
                'processed.csv', as_attachment = True,
                attachment_filename = '%s_data.csv' % subdir)

# Calling other email-api
email2api = requests.get('https://api.fullcontact.com/v2/' + 
    'person.json?email=' + email, headers={'X-FullContact-APIKey':
    ''}).json()['status']

# writing gathered data to a file
with open(file_data_processed, 'w') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fields_all)
    writer.writeheader()
    writer.writerows(final)

curtime = datetime.now(timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = '.'
################################################################################
options for mongo-classes: default, required
meta = {'indexes': [{'fields': [], 'expireAfterSeconds': 60}]}
doc.save(cascade=True)
doc.delete()
Collectively use {from_json(), to_json()} to oversome archiving issue
