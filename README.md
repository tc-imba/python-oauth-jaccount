# python-oauth-jaccount

[![PyPI version](https://badge.fury.io/py/oauth-jaccount.svg)](https://badge.fury.io/py/oauth-jaccount)

## Installation

```bash
pip install oauth-jaccount
```

Or add `oauth-jaccount` into `requirements.txt`.

## Usage (Example)

```python
from oauth_jaccount import JaccountClient

client = JaccountClient(client_id="client_id", client_secret="client_secret")

# Suppose you are using flask-like web framework
from flask import redirect, session
from your_great_project import app

# The redirect url must be the same in both authorization and get_token!
REDIRECT_URL = "https://example.com/jaccount/auth"

# This route is used by user
@app.get("/jaccount/login")
def jaccount_login():
    url, state = client.get_authorize_url(REDIRECT_URL)
    # url is the redirect url sent to the browser
    # state is a random string, you can save it to verify the client request
    
    # (optional but more secure) save the state in session
    session['jaccount_state'] = state
    
    return redirect(url)

# This route is used by jaccount server 
# We set it in REDIRECT_URL so that the server can redirect the browser to it 
# The server will send back the random state and a code
@app.get("/jaccount/auth")
def jaccount_auth(state: str, code: str):
    # (optional but more secure) verify the state in session
    if state != session.get('jaccount_state', ''):
        return redirect("url after login error")
        
    access_token, refresh_token, id_token = client.get_token(code, REDIRECT_URL)
    # access_token is used for api calls (has an expire time)
    # refresh_token can get a new access_token with refreshed expire time
    
    # id_token is a dict (parsed from jwt) with the basic information of a user
    # the format is defined by
    # {
    #   aud: str   # client_id
    #   iss: str   # 'https://jaccount.sjtu.edu.cn/oauth2/'
    #   sub: str   # jaccount username
    #   exp: str   # expiration time (UNIX epoch)
    #   iat: str   # issue time (UNIX epoch)
    #   name: str  # real name
    #   code: str  # seems empty?
    #   type: str  # jaccount type (student/faculty/alumni)
    # }
    
    # usually id_token is enough for your application
    # If you want to call other jaccount apis, you can use
    result = client.call_rest_api(access_token, JaccountClient.API.PROFILE)
    # most jaccount id/secret can only access a limited range of apis (e.g., API.PROFILE)
    # the API list in JaccountClient.API is copied from an old version of jaccount documentation
    # they are not guaranteed to work properly in the future
    
    return redirect("url after login")

# This route is used by user, use it to clear jaccount cookies
# If you do not logout the user before new user login,
# there will be a problem: since the cookies are not cleared, 
# the jaccount server will induce that the previous user is still active,
# so that the username/password page will be skipped and the previous user logins directly
@app.get("/jaccount/logout")
def jaccount_logout():
    # note that this redirect_url is usually different from REDIRECT_URL
    redirect_url = "url after logout"
    url = client.get_logout_url(redirect_url)
    return redirect(url)

```

## Advance Usage

`get_token` and `call_rest_api` have more flexible version: `get_token_url` and `get_rest_api_url`. You can use them to get the corresponding urls if you want to call them by yourselves (e.g., use `aiohttp` to make async requests).

You may check the source code for details.


## License

MIT
