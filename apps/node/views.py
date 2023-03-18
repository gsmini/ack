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


class NodeViewSet(mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    authentication_classes = []

    permission_classes = []

    def list(self, request, *args, **kwargs):
        data = k8s_client.list_namespace()
        return Response(data)
