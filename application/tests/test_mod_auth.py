import pytest
from application.mod_auth.models import User
from application.tests.test_application import client

def test_signup(client):
    # when everything is done right
    payload = {'username':'test', 'email':'tes@portal.com', \
        'first_name':'test', 'last_name':'test', 'password':'123'}
    res = client.post('/auth/signup/', data=payload)    
    assert 'Account Created Successfully' in str(res.data)

    # if form is incorrect
    payload = {'username':'test', 'first_name':'test', \
        'last_name':'test', 'password':'123'}
    res = client.post('/auth/signup/', data=payload)    
    assert 'Form submitted was invalid' in str(res.data)

    # if user tries to sign up with a already existing user's info
    payload = {'username':'test', 'email':'tes@portal.com', \
        'first_name':'test', 'last_name':'test', 'password':'123'}
    res = client.post('/auth/signup/', data=payload)    
    assert 'Account Creation was Unsuccessfull' in str(res.data)
    