from django.contrib.auth.views import LoginView


class LoginWithCookie(LoginView):

    def form_invalid(self, form):

        response = super(LoginWithCookie, self).form_invalid(form)

        try:
            response.delete_cookie('JSESSIONID', path='/', domain='transkribus.eu')
        except (ValueError, TypeError, AttributeError) as error:
            logging.error("%r", error)
        finally:
            return response

    def form_valid(self, form):

        # NOTE: super.form_valid is where user is authenticated
        response = super(LoginWithCookie, self).form_valid(form)

        try:
            self.set_cookie(self.request, response)
        except (ValueError, TypeError, AttributeError) as error:
            logging.error("%r", error)

        return response

    def set_cookie(self, request, response):

        user = self.request.user
        transkribus = user.tsdata

        # Set-Cookie: JSESSIONID=""; Domain=transkri…nly; Path=/TrpServer/; Secure
        response.set_cookie(
            'JSESSIONID', value=transkribus.sessionId,
            path='/TrpServer/', domain='transkribus.eu',
            httponly=False, secure=True)
