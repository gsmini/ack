import yaml
from rest_framework import viewsets, status
import common.mixins as mixins
from libs.k8s import k8s_client
from common.response import MyResponse as Response
from .serializers import YamlCreateSerializer


class PodYamlViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = []

    def list(self, request, *args, **kwargs):
        name = self.request.query_params.get("name", "")
        namespace = self.request.query_params.get("namespace", "")
        data = k8s_client.get_yaml_for_pod(name, namespace)
        return Response(data)


class DeploymentYamlViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = []

    def list(self, request, *args, **kwargs):
        name = self.request.query_params.get("name", "")
        namespace = self.request.query_params.get("namespace", "")

        data = k8s_client.get_yaml_for_deployment(name, namespace)

        return Response(data)


class ApplyYamlViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    authentication_classes = []
    permission_classes = []
    serializer_class = YamlCreateSerializer

    def perform_create(self, serializer):
        file_obj = serializer.validated_data.get("file")
        context = file_obj.read()
        yaml_dict = yaml.load(context, Loader=yaml.FullLoader)
        k8s_client.apply_yaml([yaml_dict])
        return None
