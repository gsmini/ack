from django.shortcuts import render
import requests
from django.contrib.auth import get_user_model, authenticate
from rest_framework import viewsets
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
import common.mixins as mixins
from libs.k8s import k8s_client
from common.response import MyResponse as Response


class DeploymentViewSet(
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
            data, _continue = k8s_client.list_deployment_for_all_namespaces(
                limit, start
            )
            resp["data"] = data
            resp["_continue"] = _continue
        else:
            data, _continue = k8s_client.list_namespaced_deployment(
                limit, start, namespace
            )
            resp["data"] = data
            resp["_continue"] = _continue

        return Response(resp)

    def retrieve(self, request, *args, **kwargs):
        name = self.kwargs.get(self.lookup_field, "")
        namespace = self.request.query_params.get("namespace", "")
        print(name, print(namespace))
        data = k8s_client.read_deployment(name, namespace)
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        ns_name = self.kwargs.get(self.lookup_field, "")
        data = k8s_client.delete_namespace(ns_name)
        return Response(status=data)
