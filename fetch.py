import os
import sys
from requests import get as GET
from csv import DictWriter, reader as csvReader

if __name__ == '__main__':
    
    # Get paths
    homedir = os.path.dirname(os.path.abspath(__file__))
    jobdir = str(sys.argv[1])
    
    # Final fields
    fields_phone = ['P_name', 'P_confidence', 'P_gender', 'P_gender_confidence',
                    'P_address', 'P_email', 'P_fb_id', 'P_fb_name',
                    'P_fb_imageurl']
    fields_email = ['E_dob', 'E_gender', 'E_googleid', 'E_name', 'E_photo',
                    'E_friends', 'E_extrainfocount']
    fields_all = fields_phone + fields_email
    with open(os.path.join(jobdir, 'raw.csv')) as fin,\
         open(os.path.join(jobdir, 'processed.csv'), 'w') as fout:
        # Open read andwrite views of files
        writer = DictWriter(fout, fieldnames=fields_all)
        reader = csvReader(fin, delimiter=',')
        writer.writeheader()
        for i, line in enumerate(reader):
            currow = {}
            
            # Calling phone-api
            phone = line[0]
            phoneapi = GET(('https://truecheckr.com/api/phone-api?apiKey='
                            'BC9c7ZVWp6dTdMa4HCzrItFP4r7rDprLGdsWHWL6zuw'
                            '&phone_num=91%s' % phone)).json()['status']
            if ('code' in phoneapi) and (phoneapi['code'] == 0):
                # successful
                try:
                    data = phoneapi['data']['value']
                    if 'name' in data:
                        currow['P_name'] = data['name']
                    if 'confidence' in data:
                        currow['P_confidence'] = data['confidence']
                    
                    if 'gender_details' in data:
                        if len(data['gender_details'])>0:
                            tdata = data['gender_details'][0]
                            if 'gender' in tdata:
                                currow['P_gender'] = tdata['gender']
                            if 'score' in tdata:
                                currow['P_gender_confidence'] = tdata['score']
                    
                    if ('location_details' in data) and \
                            (len(data['location_details']) > 0):
                        currow['P_address'] = data['location_details'][0]['city']

                    if 'social_details' in data:
                        tdata = data['social_details']
                        if 'email' in tdata[0]:
                            currow['P_email'] = tdata[0]['email']
                        if 'facebook_id' in tdata[1]:
                            currow['P_fb_id'] = tdata[1]['facebook_id']
                        if 'facebook_name' in tdata[1]:
                            currow['P_fb_name'] = tdata[1]['facebook_name']
                        if 'facebook_image' in tdata[1]:
                            currow['P_fb_imageurl'] = tdata[1]['facebook_image']
                except:
                    pass

            # Calling email-api
            email = line[1]
            emailapi = GET(('https://www.truecheckr.com/api/searchemail-api?'
                            'email=%s&apiKey=Ie5JtImyHR9ORznuJLCocVP5ryURpz0Q'
                            'v8gt44fTf1Q' % email)).json()['status']
            if ('code' in emailapi) and (emailapi['code'] == 0):
                # successful
                try:
                    data = emailapi['data']['googleapis']
                    ecdata = emailapi['data']['email_check']
                    if 'birthday' in data:
                        currow['E_dob'] = data['birthday']
                    if 'gender' in data:
                        currow['E_gender'] = data['gender']
                    elif 'gender' in ecdata:
                        currow['E_gender'] = ecdata['gender']
                    if 'id' in data:
                        currow['E_googleid'] = data['id']
                    if 'displayName' in data:
                        currow['E_name'] = data['displayName']
                    if 'image' in data:
                        if 'isDefault' in data['image']:
                            if not data['image']['isDefault']:
                                currow['E_photo'] = data['image']['url']
                    if ('isPlusUser' in data) and data['isPlusUser']:
                        if 'circledByCount' in data:
                            currow['E_friends'] = data['circledByCount']
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
                        currow['E_extrainfocount'] = extras
                except:
                    pass

            # Calling other email-api
            # email2api = GET(
            #     'https://api.fullcontact.com/v2/person.json?email=%s' % email,
            #     headers = { 'X-FullContact-APIKey':
            #     'CYUduQUw2hKkPTotMEDrgqRAqU2j8Svz'}).json()['status']

            writer.writerow(currow)

