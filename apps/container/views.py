from rest_framework import viewsets
import common.mixins as mixins
from libs.k8s import k8s_client
from common.response import MyResponse as Response


class ContainerViewSet(mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = []

    def list(self, request, *args, **kwargs):
        resp = dict()
        limit = int(self.request.query_params.get("limit", 10))
        start = self.request.query_params.get("start", "")
        namespace = self.request.query_params.get("namespace", "")

        data, _continue = k8s_client.list_containers_for_all_pod(limit, start, namespace)
        resp['data'] = data
        resp['_continue'] = _continue

        return Response(resp)
