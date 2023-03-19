from rest_framework import serializers


class YamlCreateSerializer(serializers.Serializer):
    file = serializers.FileField(
        help_text="上传文件对象",
        required=True,
        allow_empty_file=False,
        error_messages={
            "allow_empty_file": "文件内容为空",
            "required": "该字段必传",
            "allow_blank": "该字段必填",
        },
    )
