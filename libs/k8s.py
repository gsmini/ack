import pprint

from kubernetes import client, config
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
        self.client_apps = client.AppsV1Api(self.api_client)
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
        return res

    def list_namespace(self, limit="10", start=""):
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

    def delete_namespace(self, name=""):
        if not name:
            raise MyValidationError(message="参数错误", code=10001)
        try:
            res = self.core_v1_api.delete_namespace(name=name)
            # todo处理自己的数据逻辑
        except RequestError as e:
            raise MyValidationError(message="请求链接错误", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10004)
        return res

    def read_namespace(self, name=""):
        if not name:
            raise MyValidationError(message="参数错误", code=10001)
        try:
            res = self.core_v1_api.read_namespace(name=name)
        except RequestError as e:
            raise MyValidationError(message="请求链接错误", code=10000)
        except ApiException as e:
            raise MyValidationError(message=e.body, code=10005)
        return res


k8s_client = K8sClient()
if __name__ == "__main__":
    myclient = K8sClient()
    # pprint.pprint(myclient.create_namespace("gsmini"))
    pprint.pprint(myclient.list_namespace())
    # pprint.pprint(myclient.read_namespace())
    # pprint.pprint(myclient.delete_namespace())
    # pprint.pprint(myclient.create_namespace_by_yaml())
