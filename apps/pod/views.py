from rest_framework import viewsets
import common.mixins as mixins
from libs.k8s import k8s_client
from common.response import MyResponse as Response


class PodViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = []
    permission_classes = []

    def list(self, request, *args, **kwargs):
        resp = dict()
        limit = int(self.request.query_params.get("limit", 10))
        start = self.request.query_params.get("start", "")
        namespace = self.request.query_params.get("namespace", "")
        if not namespace:
            data, _continue = k8s_client.list_pod_for_all_namespaces(limit, start)
            resp["data"] = data
            resp["_continue"] = _continue
        else:
            data, _continue = k8s_client.list_namespaced_pod(limit, start, namespace)
            resp["data"] = data
            resp["_continue"] = _continue

        return Response(resp)

    def destroy(self, request, *args, **kwargs):
        name = self.kwargs.get(self.lookup_field, "")
        namespace = self.request.query_params.get("namespace", "")
        data = k8s_client.delete_namespaced_pod(name, namespace)
        return Response(status=data)


class PodLogViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = []
    permission_classes = []

    def list(self, request, *args, **kwargs):
        resp = dict()

        return Response(resp)
