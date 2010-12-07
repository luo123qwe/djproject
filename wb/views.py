#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
..django.....oauth views
..django.session..
"""

from django.http import HttpResponseRedirect,HttpResponse

from weibopy import OAuthHandler, oauth, WeibopError

consumer_key = '1042005553' # ......appkey
consumer_secret = '298d6a10fd7c1b694a25f627ee785669' # ......appkey...secret

class WebOAuthHandler(OAuthHandler):
    
    def get_authorization_url_with_callback(self, callback, signin_with_twitter=False):
        """Get the authorization URL to redirect the user"""
        try:
            # get the request token
            self.request_token = self._get_request_token()

            # build auth request and return as url
            if signin_with_twitter:
                url = self._get_oauth_url('authenticate')
            else:
                url = self._get_oauth_url('authorize')
            request = oauth.OAuthRequest.from_token_and_callback(
                token=self.request_token, callback=callback, http_url=url
            )
            return request.to_url()
        except Exception, e:
            raise WeibopError(e)


def _get_referer_url(request):
    referer_url = request.META.get('HTTP_REFERER', '/')
    host = request.META['HTTP_HOST']
    if referer_url.startswith('http') and host not in referer_url:
        referer_url = '/' # ..................
    return referer_url

def _oauth():
    """..oauth..."""
    return WebOAuthHandler(consumer_key, consumer_secret)

def login(request):
    # .......url............
    if request.session.get('oauth_access_token'):
        return HttpResponse("yes,<a href='/wb/logout/'>logout</a>")
    back_to_url = _get_referer_url(request)
    request.session['login_back_to_url'] = back_to_url
    
    # ..oauth..url
    login_backurl = request.build_absolute_uri('/wb/login_check')
    auth_client = _oauth()
    auth_url = auth_client.get_authorization_url_with_callback(login_backurl)
    # ..request_token..............access_token
    request.session['oauth_request_token'] = auth_client.request_token
    # .......
    return HttpResponseRedirect(auth_url)
    
def login_check(request):
    """...................access_token....."""
    # http://mk2.com/?oauth_token=c30fa6d693ae9c23dd0982dae6a1c5f9&oauth_verifier=603896
    verifier = request.GET.get('oauth_verifier', None)
    auth_client = _oauth()
    # .......session.request_token
    request_token = request.session['oauth_request_token']
    del request.session['oauth_request_token']
    
    auth_client.set_request_token(request_token.key, request_token.secret)
    access_token = auth_client.get_access_token(verifier)
    # ..access_token.........access_token..
    request.session['oauth_access_token'] = access_token
    
    # ...........
    return HttpResponseRedirect('/wb/')

def logout(request):
    """.........access_token"""
    del request.session['oauth_access_token']
    back_to_url = _get_referer_url(request)
    return HttpResponseRedirect(back_to_url)
