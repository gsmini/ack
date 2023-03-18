from rest_framework import viewsets
import common.mixins as mixins
from libs.k8s import k8s_client
from common.response import MyResponse as Response


class EventViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    authentication_classes = []

    permission_classes = []

    def list(self, request, *args, **kwargs):
        resp = dict()
        limit = self.request.query_params.get("limit", "10")
        start = self.request.query_params.get("start", "")
        data, _continue = k8s_client.list_namespaced_event(limit, start)
        resp['data'] = data
        resp['_continue'] = _continue
        return Response(resp)

