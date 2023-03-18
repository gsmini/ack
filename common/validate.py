from rest_framework.exceptions import APIException, _get_error_details


class MyValidationError(APIException):
    status_code = 200
    default_detail = ('Invalid input.')
    default_code = 'invalid'

    def __init__(self, detail=None, code=600):
        if detail is None:
            detail = self.default_detail
        # 封装错误返回体
        data = {
            'code': 600,
            'status': 'fail',
            'message': detail,  # raise 的业务错误内容
            'results': {}
        }

        self.detail = _get_error_details(data, code)
