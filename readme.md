## INTRODUCTION

Here is an overview of steps taking place:

#### index.py

- Gives the user a unique `TaskId`
- Creates a separate folder named `TaskId` in `Data/`
- Places a copy of the uploaded file in the created folder
- Creates a `info.json` file with all the user inputs in the same folder
- Calls `python fetch.py TaskId` and exits

#### fetch.py

- Opens the json file containing relevant informations to carry out the process
- Creates a `processed.csv` file in `Data\TaskId` where it stores the relevant data
fetched from several API calls
- Calls `python send.py TaskId` and exits

#### INSTALLATION

https://www.datasciencebytes.com/bytes/2015/02/24/running-a-flask-app-on-aws-ec2/

##### PIP Packages

Flask-PyMongo


#### TO-DO

https://www.googleapis.com/customsearch/v1?q=software+engineer+goldman+sachs+new+york&cx=017553353235391622345%3Arweq6qwp_um&key=AIzaSyAbWlmDLuv9TIXVxF6ucu0NE8hf0xTxBpw