import pprint

from kubernetes import client, config, utils
import yaml

from common.validate import MyValidationError
from urllib3.exceptions import RequestError
from kubernetes.client.exceptions import ApiException
from django.conf import settings


# 本地调试远程集群的时候我只用的pycharm ssh interpreter的方式是用的我k8s集群master节点上的python
# 这样我就不用把k8s的config文件copy了，master节点的文件位置：/etc/kubernetes/admin.conf这个地方
# k8s client的是用文档：
# https://www.modb.pro/db/438213
# https://blog.csdn.net/sinat_33431419/article/details/105223726
# 官方文档：https://github.com/kubernetes-client/python/blob/master/kubernetes/README.md
# 修改apiserver admin.conf外网访问：https://zhuanlan.zhihu.com/p/505324148


class K8sClient:

    def __init__(self):
        config.load_kube_config(settings.KUBE_CONFIG)
        self.api_client = client.ApiClient()  # 底层的apiclient
        # 各个资源操作对象需要声明不同的client，具体看github readme.md中的文档即可，可做工具书查询。
        self.core_v1_api = client.CoreV1Api(self.api_client)
        self.apps_client = client.AppsV1Api(self.api_client)
        # self.client_networking = client.NetworkingApi(self.v1client)

    def create_namespace(self, name=""):
        if not name:
            raise MyValidationError(message="参数错误", code=10001)
        try:
            body = client.V1Namespace(kind="Namespace", api_version="v1", metadata={"name": name})
            res = self.core_v1_api.create_namespace(body, pretty=True)
        except RequestError as e:
            raise MyValidationError(message="请求链接错误", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10001)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)
        return res

    def create_namespace_by_yaml(self):
        try:
            with open("./yaml/namespace.yaml") as file:
                body = yaml.safe_load(file)
                res = self.core_v1_api.create_namespace(body)
        except RequestError as e:
            raise MyValidationError(message="请求链接错误", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10002)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)
        return res

    def list_namespace(self, limit=10, start=""):
        """

        :param limit: 没次请求返回的个数
        :param start: 从上次请求的位置开始，类似mysql的offset功能
        :return: 返回查询数据以及当次请求的截止位置标记_continue的值
        """

        kwargs = dict()
        kwargs["limit"] = limit
        if start:
            kwargs["_continue"] = start
        try:
            res = self.core_v1_api.list_namespace(**kwargs)
            result = []
            for item in res.items:
                data = dict()
                data["name"] = item.metadata.name
                data["phase"] = item.status.phase
                data["creation_timestamp"] = item.metadata.creation_timestamp
                data["labels"] = item.metadata.labels
                result.append(data)
            # 用来实现分页查询的类似offset标记
            _continue = res.metadata._continue if res.metadata._continue else None
            return result, _continue
        # 请求不通
        except RequestError as e:
            raise MyValidationError(message="请求链接错误", code=10000)
        # 业务逻辑错误
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10003)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)

    def delete_namespace(self, name=""):
        if not name:
            raise MyValidationError(message="参数错误", code=10001)
        try:
            self.core_v1_api.delete_namespace(name=name)
            return None
            # todo处理自己的数据逻辑
        except RequestError as e:
            raise MyValidationError(message="请求链接错误", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10004)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)

    def read_namespace(self, name=""):
        if not name:
            raise MyValidationError(message="参数错误", code=10001)
        try:
            res = self.core_v1_api.read_namespace(name=name)
            data = dict()
            data["name"] = res.metadata.name
            data["creation_timestamp"] = res.metadata.creation_timestamp
            data["uid"] = res.metadata.uid
            data["labels"] = res.metadata.labels
            return data
        except RequestError as e:
            raise MyValidationError(message="请求链接错误", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)

    # 查看全部namespace下面的事件列表
    def list_event_for_all_namespaces(self, limit=10, start=""):
        """
        :param limit: 没次请求返回的个数
        :param start: 从上次请求的位置开始，类似mysql的offset功能
        :return: 返回查询数据以及当次请求的截止位置标记_continue的值
        """
        kwargs = dict()
        kwargs["limit"] = limit
        if start:
            kwargs["_continue"] = start

        try:
            res = self.core_v1_api.list_event_for_all_namespaces(**kwargs)
            result = []
            for item in res.items:
                data = dict()
                data["name"] = item.metadata.name  # 事件名字
                data["reason"] = item.reason  # 发生原因
                data["message"] = item.message  # 事件详情
                data["source"] = str(item.source)  # 事件来源
                data["count"] = item.count  # 发生次数
                data["first_timestamp"] = item.first_timestamp  # 第一次发生时间
                data["last_timestamp"] = item.last_timestamp  # 最后一次发生时间
                result.append(data)
            # 用来实现分页查询的类似offset标记
            _continue = res.metadata._continue if res.metadata._continue else None
            return result, _continue
        except RequestError as e:
            raise MyValidationError(message=f"请求链接错误:{e.__dict__}", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)

    # 查看某个namespace下面的事件列表
    def list_namespaced_event(self, limit=10, start="", namespace=""):
        """
        :param namespace: 命名空间的名字
        :param limit: 没次请求返回的个数
        :param start: 从上次请求的位置开始，类似mysql的offset功能
        :return: 返回查询数据以及当次请求的截止位置标记_continue的值
        """
        if not namespace:
            raise MyValidationError(message="参数错误", code=10001)
        kwargs = dict()
        kwargs["limit"] = limit
        if start:
            kwargs["_continue"] = start

        try:
            res = self.core_v1_api.list_namespaced_event(namespace=namespace, **kwargs)
            result = []
            for item in res.items:
                data = dict()
                data["name"] = item.metadata.name  # 事件名字
                data["reason"] = item.reason  # 发生原因
                data["message"] = item.message  # 事件详情
                data["source"] = str(item.source)  # 事件来源
                data["count"] = item.count  # 发生次数
                data["first_timestamp"] = item.first_timestamp  # 第一次发生时间
                data["last_timestamp"] = item.last_timestamp  # 最后一次发生时间
                result.append(data)
            # 用来实现分页查询的类似offset标记
            _continue = res.metadata._continue if res.metadata._continue else None
            return result, _continue
        except RequestError as e:
            raise MyValidationError(message=f"请求链接错误:{e.__dict__}", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)

    def list_deployment_for_all_namespaces(self, limit=10, start=""):
        kwargs = dict()
        kwargs["limit"] = limit
        if start:
            kwargs["_continue"] = start
        try:
            res = self.apps_client.list_deployment_for_all_namespaces(**kwargs)
            result = []
            for item in res.items:
                data = dict()
                images = []  # 一个pod会有多个image
                for image in item.spec.template.spec.containers:
                    images.append({"image_name": image.image})
                data["name"] = item.metadata.name
                data["namespace"] = item.metadata.namespace
                data["creation_timestamp"] = item.metadata.creation_timestamp
                data["image"] = images
                data["labels"] = item.metadata.labels
                data["replicas"] = item.status.replicas
                data["unavailable_replicas"] = item.status.unavailable_replicas if \
                    item.status.unavailable_replicas else 0

                result.append(data)
            # 用来实现分页查询的类似offset标记
            _continue = res.metadata._continue if res.metadata._continue else None
            return result, _continue
        except RequestError as e:
            raise MyValidationError(message=f"请求链接错误:{e.__dict__}", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)

    def list_namespaced_deployment(self, limit=10, start="", namespace=""):
        if not namespace:
            raise MyValidationError(message="参数错误", code=10001)
        kwargs = dict()
        kwargs["limit"] = limit
        if start:
            kwargs["_continue"] = start
        try:
            res = self.apps_client.list_namespaced_deployment(namespace=namespace, **kwargs)
            result = []
            for item in res.items:
                data = dict()
                images = []  # 一个pod会有多个image
                for image in item.spec.template.spec.containers:
                    images.append({"image_name": image.image})
                data["name"] = item.metadata.name
                data["namespace"] = item.metadata.namespace
                data["creation_timestamp"] = item.metadata.creation_timestamp
                data["image"] = images
                data["labels"] = item.metadata.labels
                data["replicas"] = item.status.replicas
                data["unavailable_replicas"] = item.status.unavailable_replicas if \
                    item.status.unavailable_replicas else 0

                result.append(data)
            # 用来实现分页查询的类似offset标记
            _continue = res.metadata._continue if res.metadata._continue else None
            return result, _continue
        except RequestError as e:
            raise MyValidationError(message=f"请求链接错误:{e.__dict__}", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)

    def read_deployment(self, name="", namespace=""):
        if not (namespace and name):
            raise MyValidationError(message="参数错误", code=10001)
        try:
            res = self.apps_client.read_namespaced_deployment(name=name, namespace=namespace)

            data = dict()

            data["metadata"] = {
                "name": res.metadata.name,
                "namespace": res.metadata.namespace,
                "uid": res.metadata.uid,
                "creation_timestamp": res.metadata.creation_timestamp,
                "labels": res.metadata.labels,
                "annotations": res.metadata.annotations
            }

            data["spec"] = {
                "replicas": res.spec.replicas,
                "strategy": res.spec.strategy.to_dict(),
                "selector": res.spec.selector.to_dict(),
                "min_ready_seconds": res.spec.min_ready_seconds,  # 最小准备秒数
                "revision_history_limit": res.spec.revision_history_limit  # 修改历史记录限制
            }
            # 滚动更新策略
            data["rolling_update"] = {
                "strategy": res.spec.strategy.to_dict(),  # 最大不可用
            }
            data["pods_status"] = {
                "available_replicas": res.status.available_replicas,  # 可用的
                "replicas": res.status.replicas,  # 总副本数
                "unavailable_replicas": res.status.unavailable_replicas,  # 不可用副本数
                "ready_replicas": res.status.ready_replicas  # 准备好的副本数
            }
            # 比如要转成dict才能序列化成json返回给前端
            data["status"] = [condition.to_dict() for condition in res.status.conditions]

            return data
        except RequestError as e:
            raise MyValidationError(message=f"请求链接错误:{e.__dict__}", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)

    # 查看pod列表 必须带namespace
    def list_namespaced_pod(self, limit=10, start="", namespace=""):
        if not namespace:
            raise MyValidationError(message="参数错误", code=10001)
        kwargs = dict()
        kwargs["limit"] = limit
        if start:
            kwargs["_continue"] = start
        try:
            res = self.core_v1_api.list_namespaced_pod(namespace, **kwargs)
            result = []
            for item in res.items:
                data = dict()
                data["name"] = item.metadata.name  # 名字
                data["namespace"] = item.metadata.namespace  # 命名空间
                data["creation_timestamp"] = item.metadata.creation_timestamp  # 创建时间
                data["node_name"] = item.spec.node_name  # 节点名字
                data["labels"] = item.metadata.labels  # 标签
                data["images"] = [container.image for container in item.spec.containers]  # pod内的镜像
                # 里面会有很多image 所以我做成一个list展示每个container的状态信息
                containers_data = []
                for container in item.status.container_statuses:
                    status = ""
                    reason = ""
                    state_dict = container.state.to_dict()
                    for key in state_dict.keys():
                        if state_dict.get(key):
                            status = key
                            reason = state_dict.get(key)
                    containers_data.append({
                        "image": container.image,  # 镜像名字
                        "restart_count": container.restart_count,  # 重启次数
                        "status": status,  # 当前状态
                        "reason": reason,  # 当前状态原因
                        "ready": container.ready,  # 准备就绪

                    })
                data["containers_data"] = containers_data
                result.append(data)
            # 用来实现分页查询的类似offset标记
            _continue = res.metadata._continue if res.metadata._continue else None
            return result, _continue

        except RequestError as e:
            raise MyValidationError(message=f"请求链接错误:{e.__dict__}", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)

    # 查看pod列表 必须带namespace
    def list_pod_for_all_namespaces(self, limit=10, start=""):
        kwargs = dict()
        kwargs["limit"] = limit
        if start:
            kwargs["_continue"] = start
        try:
            res = self.core_v1_api.list_pod_for_all_namespaces(**kwargs)
            result = []
            for item in res.items:
                data = dict()
                data["name"] = item.metadata.name  # 名字
                data["namespace"] = item.metadata.namespace  # 命名空间
                data["creation_timestamp"] = item.metadata.creation_timestamp  # 创建时间
                data["node_name"] = item.spec.node_name  # 节点名字
                data["labels"] = item.metadata.labels  # 标签
                data["images"] = [container.image for container in item.spec.containers]  # pod内的镜像
                # 里面会有很多image 所以我做成一个list展示每个container的状态信息
                containers_data = []
                for container in item.status.container_statuses:
                    status = ""
                    reason = ""
                    state_dict = container.state.to_dict()
                    for key in state_dict.keys():
                        if state_dict.get(key):
                            status = key
                            reason = state_dict.get(key)
                    containers_data.append({
                        "image": container.image,  # 镜像名字
                        "restart_count": container.restart_count,  # 重启次数
                        "status": status,  # 当前状态
                        "reason": reason,  # 当前状态原因
                        "ready": container.ready,  # 准备就绪

                    })
                data["containers_data"] = containers_data
                result.append(data)
            # 用来实现分页查询的类似offset标记
            _continue = res.metadata._continue if res.metadata._continue else None
            return result, _continue

        except RequestError as e:
            raise MyValidationError(message=f"请求链接错误:{e.__dict__}", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)

    # 删除pod
    def delete_namespaced_pod(self, name="", namespace=""):
        try:
            res = self.core_v1_api.delete_namespaced_pod(name, namespace)
        except RequestError as e:
            raise MyValidationError(message=f"请求链接错误:{e.__dict__}", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)
        # 查看pod详情

    def read_namespaced_pod(self):
        pass

    # 查看pod实时日志
    def read_namespaced_pod_log(self):
        pass

    # 强制重启pod
    def replace_namespaced_pod(self):
        pass

    # 交互进入pod
    def connect_post_namespaced_pod_exec(self):
        pass

    # 获取pod下面的container信息
    def list_containers_for_all_pod(self, limit=10, start="", namespace=""):
        if not namespace:
            raise MyValidationError(message="参数错误", code=10001)
        kwargs = dict()
        kwargs["limit"] = limit
        if start:
            kwargs["_continue"] = start
        try:
            res = self.core_v1_api.list_namespaced_pod(namespace, **kwargs)
            result = []

            for item in res.items:
                for container in item.spec.containers:
                    data = dict()
                    data["name"] = container.name
                    result.append(data)
            # 用来实现分页查询的类似offset标记
            _continue = res.metadata._continue if res.metadata._continue else None
            return result, _continue

        except RequestError as e:
            raise MyValidationError(message=f"请求链接错误:{e.__dict__}", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)

    # 获取当前pod资源的yaml
    def get_yaml_for_pod(self, name="", namespace=""):
        if not (namespace and name):
            raise MyValidationError(message="参数错误", code=10001)
        try:
            res = self.core_v1_api.read_namespaced_pod(name, namespace)

        except RequestError as e:
            raise MyValidationError(message=f"请求链接错误:{e.__dict__}", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)

        return yaml.safe_dump(res.to_dict())

    # 获取当前deployment资源的yaml
    def get_yaml_for_deployment(self, name="", namespace=""):
        if not (namespace and name):
            raise MyValidationError(message="参数错误", code=10001)
        try:
            res = self.apps_client.read_namespaced_deployment(name=name, namespace=namespace)

        except RequestError as e:
            raise MyValidationError(message=f"请求链接错误:{e.__dict__}", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)

        return yaml.safe_dump(res.to_dict())

    # 文件yaml方式部署资源对象
    def apply_yaml(self, yaml_objects_list=None):
        if not yaml_objects_list:
            raise MyValidationError(message="yaml文件为空", code=10001)
        try:
            res = utils.create_from_yaml(self.api_client, yaml_objects=yaml_objects_list)

        except RequestError as e:
            raise MyValidationError(message=f"请求链接错误:{e.__dict__}", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        except Exception as e:
            raise MyValidationError(message=str(e), code=20000)


k8s_client = K8sClient()
if __name__ == "__main__":
    myclient = K8sClient()
    # pprint.pprint(myclient.create_namespace("gsmini"))
    pprint.pprint(myclient.list_namespace())
    # pprint.pprint(myclient.read_namespace())
    # pprint.pprint(myclient.delete_namespace())
    # pprint.pprint(myclient.create_namespace_by_yaml())
