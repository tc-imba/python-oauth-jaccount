from urllib.parse import urlencode
from urllib.request import urlopen, Request
from json import loads
from jwt import decode
from oauthlib.oauth2 import WebApplicationClient


class JaccountClient(WebApplicationClient):
    """A client utilizing the jaccount grant workflow."""

    class API:
        PROFILE = 'v1/me/profile'
        AUTH_POSITIONS = 'v1/enterprise/user/positions'
        AUTH_RIGHTS = 'v1/enterprise/user/rights'
        EDU_LESSONS = 'v1/me/lessons'
        EDU_EXAMS = 'v1/me/examinations'

    def __init__(self, client_id, client_secret, **kwargs):
        super(JaccountClient, self).__init__(client_id)
        self.client_secret = client_secret
        self.host = kwargs.get('host', 'https://jaccount.sjtu.edu.cn/')
        self.authorize_path = kwargs.get('authorize_path', 'oauth2/authorize')
        self.access_token_path = kwargs.get('access_token_path', 'oauth2/token')
        self.logout_path = kwargs.get('logout_path', 'oauth2/logout')
        self.api_host = kwargs.get('api_host', 'https://api.sjtu.edu.cn/')

    def get_authorize_url(self, redirect_url, **kwargs):
        authorization_url = self.host + self.authorize_path
        url = self.prepare_authorization_request(
            authorization_url=authorization_url,
            redirect_url=redirect_url,
            **kwargs
        )
        state = self.state
        return url[0], state

    def get_logout_url(self, redirect_url):
        params = urlencode({'post_logout_redirect_uri': redirect_url})
        return '%s%s?%s' % (self.host,
                            self.authorize_path,
                            params)

    def get_token_url(self, code, redirect_url, **kwargs):
        token_url = self.host + self.access_token_path
        url, headers, body = self.prepare_token_request(
            token_url=token_url,
            redirect_url=redirect_url,
            code=code,
            client_secret=self.client_secret,
            **kwargs
        )
        return url, headers, body

    def get_token(self, code, redirect_url, **kwargs):
        url, headers, body = self.get_token_url(code, redirect_url, **kwargs)
        req = Request(url, headers=headers, data=body.encode('utf-8'))
        res = urlopen(req).read()
        result = loads(res.decode('utf-8'))
        id_token = decode(result['id_token'], verify=False)
        return result['access_token'], result['refresh_token'], id_token

    def get_refresh_token_url(self, refresh_token, redirect_url, **kwargs):
        token_url = self.host + self.access_token_path
        url, headers, body = self.prepare_refresh_token_request(
            token_url=token_url,
            redirect_url=redirect_url,
            refresh_token=refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
            **kwargs
        )
        return url, headers, body

    def refresh_token(self, refresh_token, redirect_url, **kwargs):
        url, headers, body = self.get_refresh_token_url(
            refresh_token, redirect_url, **kwargs)
        req = Request(url, headers=headers, data=body.encode('utf-8'))
        res = urlopen(req).read()
        result = loads(res.decode('utf-8'))
        id_token = decode(result['id_token'], verify=False)
        return result['access_token'], result['refresh_token'], id_token

    def get_rest_api_url(self, access_token, path, **kwargs):
        params = urlencode({
            'access_token': access_token,
            'client_id': self.client_id,
            **kwargs
        })
        url = '%s%s?%s' % (self.api_host,
                           path,
                           params)
        return url

    def call_rest_api(self, access_token, path, **kwargs):
        url = self.get_rest_api_url(access_token, path, **kwargs)
        res = urlopen(url).read()
        result = loads(res.decode('utf-8'))
        return result
