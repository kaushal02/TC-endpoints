from mongoengine.context_managers import switch_collection
from requests import get as GET
from helper import debug, exist
from pprint import pprint

from models.facebookpkg import Facebook
from models.genderpkg import Gender
from models.phonepkg import Phone

def phoneapi(val):
    try:
        prev = Phone.objects.get(pk=val)
        if prev.expired():
            print('\n\nFUCK!\n\n')
            prev.switch_collection('phoneArchived')
            prev.save()

            prev.switch_collection('phone')
            prev.delete()
            # with switch_collection(Phone, 'phoneArchived') as PhoneArchived:
            #     PhoneArchived(self=prev).save()
            collect(val)
    except Phone.DoesNotExist:
        print('\n\nDamn!\n\n')
        collect(val)

def collect(val):
    try:
        Phone.objects.get(pk=val).delete()
    except:
        print('\n\nTried deleting? ...sure!\n\n')
    else:
        print('\n\nDeleted!\n\n')
    pdata = Phone(pk=val)
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
        except:
            pass
        else:
            #confidence
            if exist(data, 'confidence'):
                pdata.confidence = data['confidence']
            #name
            if exist(data, 'name'):
                pdata.name = data['name']
            #email
            if exist(data, 'social_details'):
                tdata = data['social_details'][0]
                if exist(tdata, 'email'):
                    pdata.email = tdata['email']
            #address
            if 'location_details' in data:
                for location in data['location_details']:
                    if exist(location, 'city'):
                        pdata.addresses.append(location['city'])
            #gender
            try:
                tdata = data['gender_details'][0]
                gdata = Gender(ID=tdata['gender'])
                if exist(tdata, 'score'):
                    gdata.confidence = tdata['score']
                pdata.gender = gdata
            except:
                pass
            #facebook
            try:
                tdata = data['social_details'][1]
            except:
                pass
            else:
                if exist(tdata, 'facebook_id'):
                    fdata = Facebook(pk='https://fb.com/%s' % tdata['facebook_id'])
                    if exist(tdata, 'facebook_name'):
                        fdata.name = tdata['facebook_name']
                    if exist(tdata, 'facebook_image'):
                        fdata.photo = tdata['facebook_image']
                    fdata.save()
                    pdata.facebook = fdata
        finally:
            pdata.save()