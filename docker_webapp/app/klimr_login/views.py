from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import requests
import uuid
from django.middleware.csrf import get_token, CsrfViewMiddleware
from django.views.decorators.csrf import requires_csrf_token, csrf_exempt

msendpoint = "https://login.microsoftonline.com/dvfustud.onmicrosoft.com/{0}"
client_id = "0497d5e6-b462-4ef6-bb36-a13477bb5f7c"

# Create your views here.
@requires_csrf_token
def login(request):
    # TODO CSRF Protection via state field
    #return HttpResponseRedirect(msendpoint.format("oauth2/authorize?response_type=id_token&response_mode=form_post&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fxc%2F&scope=openid&client_id="+client_id+"&nonce="+str(uuid.uuid4())))
    return render(request, "klimr_login/login.html", {'secret': get_token(request), 'nonce': str(uuid.uuid4())})

@csrf_exempt
def login2(request):
    # Brief explaination of what's going on:
    # In Django, there is built in CSRF protection.
    # It's neat, but unfotunately, Microsoft sends "state" field, and
    # Django looks for "csrfmiddlewaretoken". This code is a hack to add
    # required field and validate form
    request.csrf_processing_done = False
    if 'state' in request.POST:
        request.POST = request.POST.copy()
        request.POST['csrfmiddlewaretoken'] = request.POST['state']
        csrfcheck = CsrfViewMiddleware().process_view(request, None, (), {})
        if csrfcheck:
            return csrfcheck
        else:
            return HttpResponse('42')
    else:
        return Ht

@requires_csrf_token
def getcsrftoken(request):
    return HttpResponse(get_token(request))


def oauth2token(request):
    return HttpResponse("43")
    pass


# eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJhdWQiOiIwNDk3ZDVlNi1iNDYyLTRlZjYtYmIzNi1hMTM0NzdiYjVmN2MiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9hYjNmZjkxZC1lMTBmLTQyNWUtYjE3Ny0zYjQ1NDhhZGJiNjEvIiwiaWF0IjoxNDkwMzIyNTM1LCJuYmYiOjE0OTAzMjI1MzUsImV4cCI6MTQ5MDMyNjQzNSwiYW1yIjpbIndpYSJdLCJmYW1pbHlfbmFtZSI6ItCR0YDQvtCy0YbQuNC9IiwiZ2l2ZW5fbmFtZSI6ItCY0LPQvtGA0YwiLCJpcGFkZHIiOiI2Mi43Ni42Ljc3IiwibmFtZSI6ItCR0YDQvtCy0YbQuNC9INCY0LPQvtGA0Ywg0KHQtdGA0LPQtdC10LLQuNGHIiwib2lkIjoiMDc1YzY2ZmQtNDM1Ni00ZWZkLTliYWYtMjJhNmE5MGJhNzViIiwib25wcmVtX3NpZCI6IlMtMS01LTIxLTY0NDY5NjIxNy0yNTY1MjQ2NzgwLTM0MzQ0MTA4NzEtNzUxMDUiLCJwbGF0ZiI6IjE0Iiwic3ViIjoiOVJMNHlma2hTYTdQc3RYRDFFSy0ybV9UbFo4c25ITlM0NlpwVERvRm1BQSIsInRpZCI6ImFiM2ZmOTFkLWUxMGYtNDI1ZS1iMTc3LTNiNDU0OGFkYmI2MSIsInVuaXF1ZV9uYW1lIjoiYnJvdnRjaW4uaXNAc3R1ZGVudHMuZHZmdS5ydSIsInVwbiI6ImJyb3Z0Y2luLmlzQHN0dWRlbnRzLmR2ZnUucnUiLCJ2ZXIiOiIxLjAifQ.
# eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJhdWQiOiIwNDk3ZDVlNi1iNDYyLTRlZjYtYmIzNi1hMTM0NzdiYjVmN2MiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9hYjNmZjkxZC1lMTBmLTQyNWUtYjE3Ny0zYjQ1NDhhZGJiNjEvIiwiaWF0IjoxNDkwMzIyNjExLCJuYmYiOjE0OTAzMjI2MTEsImV4cCI6MTQ5MDMyNjUxMSwiYW1yIjpbIndpYSJdLCJmYW1pbHlfbmFtZSI6ItCR0YDQvtCy0YbQuNC9IiwiZ2l2ZW5fbmFtZSI6ItCY0LPQvtGA0YwiLCJpcGFkZHIiOiI2Mi43Ni42Ljc3IiwibmFtZSI6ItCR0YDQvtCy0YbQuNC9INCY0LPQvtGA0Ywg0KHQtdGA0LPQtdC10LLQuNGHIiwib2lkIjoiMDc1YzY2ZmQtNDM1Ni00ZWZkLTliYWYtMjJhNmE5MGJhNzViIiwib25wcmVtX3NpZCI6IlMtMS01LTIxLTY0NDY5NjIxNy0yNTY1MjQ2NzgwLTM0MzQ0MTA4NzEtNzUxMDUiLCJwbGF0ZiI6IjE0Iiwic3ViIjoiOVJMNHlma2hTYTdQc3RYRDFFSy0ybV9UbFo4c25ITlM0NlpwVERvRm1BQSIsInRpZCI6ImFiM2ZmOTFkLWUxMGYtNDI1ZS1iMTc3LTNiNDU0OGFkYmI2MSIsInVuaXF1ZV9uYW1lIjoiYnJvdnRjaW4uaXNAc3R1ZGVudHMuZHZmdS5ydSIsInVwbiI6ImJyb3Z0Y2luLmlzQHN0dWRlbnRzLmR2ZnUucnUiLCJ2ZXIiOiIxLjAifQ.