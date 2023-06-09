from rest_framework import viewsets
import common.mixins as mixins
from libs.k8s import k8s_client
from common.response import MyResponse as Response


class EventViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = []

    permission_classes = []

    def list(self, request, *args, **kwargs):
        resp = dict()
        limit = int(self.request.query_params.get("limit", 10))
        start = self.request.query_params.get("start", "")
        namespace = self.request.query_params.get("namespace", "")
        if namespace:
            data, _continue = k8s_client.list_namespaced_event(limit, start, namespace)
            resp["data"] = data
            resp["_continue"] = _continue
        else:
            data, _continue = k8s_client.list_event_for_all_namespaces(limit, start)
            resp["data"] = data
            resp["_continue"] = _continue

        return Response(resp)
