from urllib.parse import urlencode
from urllib.request import urlopen, Request
from json import loads
from jwt import decode

# from oauthlib.oauth2.rfc6749.parameters import prepare_grant_uri, \
#     prepare_token_request
from oauthlib.oauth2 import WebApplicationClient


class JaccountClient(WebApplicationClient):
    """A client utilizing the jaccount grant workflow."""

    __default_config = {
        'client_id': None,
        'client_secret': None,
        'host': 'https://jaccount.sjtu.edu.cn/',
        'authorize_path': 'oauth2/authorize',
        'access_token_path': 'oauth2/token',
        'logout_path': 'oauth2/logout',
        'api_host': 'https://api.sjtu.edu.cn/',
        'profile_path': 'v1/me/profile'
    }

    def __init__(self, client_id, client_secret, **kwargs):
        super(JaccountClient, self).__init__(client_id)
        self.client_secret = client_secret
        self.host = kwargs.get('host', 'https://jaccount.sjtu.edu.cn/')
        self.authorize_path = kwargs.get('authorize_path', 'oauth2/authorize')
        self.access_token_path = kwargs.get('access_token_path', 'oauth2/token')
        self.logout_path = kwargs.get('logout_path', 'oauth2/logout')
        self.api_host = kwargs.get('api_host', 'https://api.sjtu.edu.cn/')
        self.profile_path = kwargs.get('profile_path', 'v1/me/profile')

    # def prepare_request_uri(self, uri, redirect_uri=None, scope=None,
    #                         state=None, **kwargs):
    #     """Prepare the jaccount request URI"""
    #     if 'response_type' not in kwargs:
    #         kwargs['response_type'] = 'code'
    #     return prepare_grant_uri(uri, self.client_id,
    #                              redirect_uri=redirect_uri, scope=scope,
    #                              state=state, **kwargs)
    #
    # def prepare_request_body(self, code=None, redirect_uri=None, body='',
    #                          include_client_id=True,
    #                          grant_type='authorization_code',
    #                          **kwargs):
    #     """Prepare the access token request body."""
    #     code = code or self.code
    #     if 'client_id' in kwargs and kwargs['client_id'] != self.client_id:
    #         raise ValueError("`client_id` was supplied as an argument, but "
    #                          "it does not match `self.client_id`")
    #
    #     kwargs['client_id'] = self.client_id
    #     kwargs['include_client_id'] = include_client_id
    #     return prepare_token_request(grant_type, code=code, body=body,
    #                                  redirect_uri=redirect_uri, **kwargs)
    #
    # def prepare_authorization_implicit(self, redirect_url, scope='basic',
    #                                    **kwargs):
    #     authorization_url = self.host + self.authorize_path
    #     url = self.prepare_authorization_request(
    #         authorization_url=authorization_url,
    #         redirect_url=redirect_url,
    #         response_type='token',
    #         scope=scope,
    #         client_secret=self.client_secret,
    #         **kwargs
    #     )
    #     state = self.state
    #     return url[0], state

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
        )
        return url, headers, body

    def get_token(self, code, redirect_url, **kwargs):
        url, headers, body = self.get_token_url(code, redirect_url, **kwargs)
        req = Request(url, headers=headers, data=body.encode('utf-8'))
        res = urlopen(req).read()
        result = loads(res.decode('utf-8'))
        id_token = decode(result['id_token'], verify=False)
        return result['access_token'], result['refresh_token'], id_token

    def get_refresh_token_url(self, refresh_token, redirect_url):
        token_url = self.host + self.access_token_path
        url, headers, body = self.prepare_refresh_token_request(
            token_url=token_url,
            redirect_url=redirect_url,
            refresh_token=refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        return url, headers, body

    def refresh_token(self, refresh_token, redirect_url):
        url, headers, body = self.get_refresh_token_url(refresh_token,
                                                        redirect_url)
        req = Request(url, headers=headers, data=body.encode('utf-8'))
        res = urlopen(req).read()
        result = loads(res.decode('utf-8'))
        id_token = decode(result['id_token'], verify=False)
        return result['access_token'], result['refresh_token'], id_token

    def get_profile_url(self, access_token):
        params = urlencode({
            'access_token': access_token,
            'client_id': self.client_id,
            'scope': 'essential'
        })
        url = '%s%s?%s' % (self.api_host,
                           self.profile_path,
                           params)
        return url

    def get_profile(self, access_token):
        url = self.get_profile_url(access_token)
        print(url)
        res = urlopen(url).read()
        result = loads(res.decode('utf-8'))
        return result
