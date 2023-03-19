from rest_framework.pagination import PageNumberPagination
from django.utils.translation import gettext_lazy as _
from collections import OrderedDict, namedtuple

from .response import MyResponse as Response


class MyPageNumberPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    page_query_param = "page"
    page_query_description = _("返回第几页")
    page_size_query_description = _("每页的数量.")

    def get_paginated_response(self, data):
        """
        封装list返回
        """
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )
