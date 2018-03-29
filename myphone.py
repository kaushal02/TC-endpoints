from pprint import pprint
from myfunc import empty, debug
from requests import get as GET

def phoneapi(val):
    fields = ['name', 'confidence', 'gender', 'gender_confidence', 'address',
              'email', 'fb_id', 'fb_name', 'fb_imageurl', 'value']
    pdata = {'value': val}
    # Calling phone-api
    Key = 'aEUWnEPie64GQbEDa7rjs1fbMlm1dTnwLSt0SIqaguQ'
    data = GET(('https://truecheckr.com/api/phone-api?apiKey=%s&'
                'phone_num=91%s' % (Key, val))).json()['status']
    if ('code' in data) and (data['code'] == 0):
        # successful
        if debug:
            pprint(data)
        try:
            data = data['data']['value']
            if 'name' in data:
                pdata['name'] = data['name']
            if 'confidence' in data:
                pdata['confidence'] = data['confidence']
            
            if 'gender_details' in data:
                if len(data['gender_details'])>0:
                    tdata = data['gender_details'][0]
                    if 'gender' in tdata:
                        pdata['gender'] = tdata['gender']
                    if 'score' in tdata:
                        pdata['gender_confidence'] = tdata['score']
            
            if ('location_details' in data) and \
                    (len(data['location_details']) > 0):
                pdata['address'] = data['location_details'][0]['city']

            if 'social_details' in data:
                tdata = data['social_details']
                if 'email' in tdata[0]:
                    pdata['email'] = tdata[0]['email']
                if 'facebook_id' in tdata[1]:
                    pdata['fb_id'] = tdata[1]['facebook_id']
                if 'facebook_name' in tdata[1]:
                    pdata['fb_name'] = tdata[1]['facebook_name']
                if 'facebook_image' in tdata[1]:
                    pdata['fb_imageurl'] = tdata[1]['facebook_image']
            for field in fields:
                try:
                    if empty(pdata[field]):
                        del pdata[field]
                except:
                    pass
            return pdata
        except:
            pass
    return None
