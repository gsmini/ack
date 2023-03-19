from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from apps.namespace import views as namespace_view
from apps.event import views as event_view
from apps.deployment import views as deployment_view
from apps.pod import views as pod_view
from apps.container import views as container_view
from apps.ackyaml import views as yaml_view

router = DefaultRouter(trailing_slash=False)
router.register(r'namespace', namespace_view.NameSpaceViewSet, basename='namespace')
router.register(r'event', event_view.EventViewSet, basename='event')
router.register(r'deployment', deployment_view.DeploymentViewSet, basename='deployment')
router.register(r'pod', pod_view.PodViewSet, basename='pod')
router.register(r'pod-log', pod_view.PodLogViewSet, basename='pod-log')
router.register(r'container', container_view.ContainerViewSet, basename='container')
router.register(r'pod-yaml', yaml_view.PodYamlViewSet, basename='pod-yaml')
router.register(r'deployment-yaml', yaml_view.DeploymentYamlViewSet, basename='deployment-yaml')
router.register(r'apply-yaml', yaml_view.ApplyYamlViewSet, basename='apply-yaml')
# todo 根绝pod 查看里面的container
# todo 实时日志查看 exec交互 pod中只有一个container默认就是查看这一个 多个的话必须要指定选择目标哪一个
# todo redis分布式锁保证每次创建资源唯一 前端所有请求都要加上requestId
urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'api/v1/', include(router.urls)),
]
