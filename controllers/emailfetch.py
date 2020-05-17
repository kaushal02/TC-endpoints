from mongoengine.context_managers import switch_collection
from requests import get as GET
from datetime import datetime
from pprint import pprint
from copy import deepcopy

from models.genderpkg import Gender
from models.emailpkg import Email
from helper import debug, exist

def emailapi(val):
    try:
        prev = Email.objects.get(pk=val)
        if prev.expired():
            prev.switch_collection('emailArchived')
            prev.save()

            prev.switch_collection('email')
            prev.delete()
            # with switch_collection(Email, 'emailArchived') as EmailArchived:
            #     EmailArchived(self=prev).save()
            collect(val)
    except Email.DoesNotExist:
        collect(val)
    
def collect(val):
    try:
        Email.objects.get(pk=val).delete()
    except:
        pass
    edata = Email(pk=val)
    # Calling email-api
    Key = ''
    data = GET(('https://www.truecheckr.com/api/searchemail-api?'
                'email=%s&apiKey=%s' % (val, Key))).json()['status']
    if ('code' in data) and (data['code'] == 0):
        # successful
        if debug:
            pprint(data)
        try:
            ecdata = data['data']['email_check']
            data = data['data']['googleapis']
        except:
            pass
        else:
            #name
            if exist(data, 'displayName'):
                edata.name = data['displayName']
            #gender
            if exist(data, 'gender'):
                edata.gender = Gender(ID=data['gender'])
            elif exist(ecdata, 'gender'):
                edata.gender = Gender(ID=ecdata['gender'])
            #birthday
            if exist(data, 'birthday'):
                if data['birthday'].startswith('0000'):
                    date = datetime.strptime(data['birthday'], '0000-%m-%d')
                    edata.birthday = date.strftime('%d %B')
                else:
                    date = datetime.strptime(data['birthday'], '%Y-%m-%d')
                    edata.birthday = date.strftime('%A, %d %B %Y')
            #verified
            if ('verified' in data) and data['verified']:
                gdata.verified = True
            #friends
            if exist(data, 'circledByCount'):
                edata.friends = data['circledByCount']
            #photo
            if 'image' in data:
                if 'isDefault' in data['image']:
                    if not data['image']['isDefault']:
                        edata.photo = data['image']['url']
            #profile
            if 'id' in data:
                edata.profile = "https://plus.google.com/%s" % data['id']
            #addresses
            if 'placesLived' in data:
                for place in data['placesLived']:
                    if exist(place, 'value'):
                        edata.addresses.append(place['value'])
            #external_profiles
            if 'urls' in data:
                for profile in data['urls']:
                    if exist(profile, 'value'):
                        edata.external_profiles.append(profile['value'])
            #colleges
            # if 'organizations' in data:
                # extras += len(data['organizations'])
        finally:
            edata.save()
