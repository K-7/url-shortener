from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from hashids import Hashids
import json
from core.models import UrlMapping
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect


def home(request):
    return render(request,
                  "home.html",
                  {
                  },
                  )


def get_parsed_domain(url):
    ## removing http://
    domain = url.split("//")[-1]
    ## removing www. If any other subdomain the allow
    if domain.startswith("www."):
        d = domain.split(".")
        domain = ".".join(d[1:])
    return domain


def generate_short_url(url):
    hashids = Hashids(salt=url)
    return hashids.encode(123456789)


def redirect_method(request, short_url):
    try:
        existing_url = UrlMapping.objects.get(short_url=short_url)
        return HttpResponseRedirect(existing_url.full_url)
    except UrlMapping.DoesNotExist:
        return HttpResponseRedirect('/')


class UrlMappingViewset(View):
    """REST API for creating a shortened url
    fetching list of shortened urls
    fetching original url from a shortened url
    deleting shortened-urls
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UrlMappingViewset, self).dispatch(request, *args, **kwargs)

    def get(self, request, id=''):
        """ Return list of shortened URL's
        http://localhost:8000/url_short/2
        http://localhost:8000/url_short/
        """
        returnList = []
        try:
            if id != '':
                url_obj = UrlMapping.objects.filter(id=id).first()
                if url_obj:
                    return JsonResponse(data=url_obj.to_json(), status=200)
                else:
                    return JsonResponse(data={'message': 'Bad Request : Invalid ID'}, status=400)
            else:
                for url in UrlMapping.objects.all():
                    returnList.append(url.to_json())
                return JsonResponse(data={'url_list': returnList}, status=200)
        except Exception as ex:
            return JsonResponse(data={'message': 'Internal server Error'}, status=500)

    def post(self, request, id=''):
        """ check if url is already registerd by doing a lookup on the generated
        short_url and comparing the parsed url
        http://localhost:8000/url_short/
        """
        if request.POST:
            params = request.POST
        else:
            params = json.loads(request.body)
        if 'url' not in params or params['url'] == None:
            return JsonResponse(data={'message': 'Bad Request: URL not sent as part POST request'}, status=400)

        parsed_url = get_parsed_domain(params['url'])
        short_url = generate_short_url(parsed_url)
        try:
            existing_url = UrlMapping.objects.get(short_url=short_url)
            if parsed_url == get_parsed_domain(existing_url.full_url):
                return JsonResponse(data={'message': 'Conflict: URL is already registered'}, status=409)
        except UrlMapping.DoesNotExist:
            pass

        url = UrlMapping(
            full_url=params['url'],
            short_url=short_url
        )
        url.save()
        return JsonResponse(data={'url': url.to_json()}, status=200)

    def delete(self, request, id=''):
        """ http://localhost:8000/url_short/1
        """
        if id == '':
            return JsonResponse(data={'message': 'Bad Request : Invalid ID sent'}, status=400)
        try:
            UrlMapping.objects.get(id=id).delete()
            return JsonResponse(data={'message': 'Successfully deleted !!'}, status=200)
        except UrlMapping.DoesNotExist:
            return JsonResponse(data={'message': 'Bad Request : delete URL is not present in the DB'}, status=400)
