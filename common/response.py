from rest_framework.response import Response


class MyResponse(Response):
    def __init__(self, data=None, status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        print(status)
        data = {"code": 200, "status": "success", "message": "获取数据成功", 'data': data}
        super().__init__(data=data, status=200, template_name=None, headers=None, exception=False, content_type=None)
