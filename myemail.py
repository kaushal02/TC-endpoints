from pprint import pprint
from myfunc import empty, debug
from requests import get as GET

def emailapi(val):
    fields = ['dob', 'gender', 'google_id', 'google_friends', 'highprofile', 
              'name', 'photo', 'extrainfocount']
    edata = {'value': val}
    # Calling email-api
    Key = 'Ie5JtImyHR9ORznuJLCocVP5ryURpz0Qv8gt44fTf1Q'
    data = GET(('https://www.truecheckr.com/api/searchemail-api?'
                'email=%s&apiKey=%s' % (val, Key))).json()['status']
    if ('code' in data) and (data['code'] == 0):
        # successful
        if debug:
            pprint(data)
        try:
            ecdata = data['data']['email_check']
            data = data['data']['googleapis']
            if 'birthday' in data:
                edata['dob'] = data['birthday']
            if 'gender' in data:
                edata['gender'] = data['gender']
            elif 'gender' in ecdata:
                edata['gender'] = ecdata['gender']
            if 'id' in data:
                edata['google_id'] = data['id']
            if ('isPlusUser' in data) and data['isPlusUser']:
                if 'circledByCount' in data:
                    edata['google_friends'] = data['circledByCount']
                if ('verified' in data) and data['verified']:
                    edata['highprofile'] = True
            if 'displayName' in data:
                edata['name'] = data['displayName']
            if 'image' in data:
                if 'isDefault' in data['image']:
                    if not data['image']['isDefault']:
                        edata['photo'] = data['image']['url']
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
                edata['extrainfocount'] = extras
            for field in fields:
                try:
                    if empty(edata[field]):
                        del edata[field]
                except:
                    pass
            return edata
        except:
            pass
    return None
