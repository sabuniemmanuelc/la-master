import requests
from rest_framework.generics import ListAPIView
from rest_framework.response import Response


class SearchView(ListAPIView):
    def get(self, request, *args, **kwargs):
        headers = {'Accept-Encoding': 'gzip'}
        r = requests.get(
            f'https://test.legal-data.tech/api/search?search={kwargs["string"]}',
            headers=headers,
        )
        # page = self.paginate_queryset(r.json()['list'])
        # if page is not None:
        #     return self.get_paginated_response(page)
        return Response(r.json()['list'])
