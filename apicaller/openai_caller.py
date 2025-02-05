import json

from openai.types.chat.chat_completion_message_tool_call import Function

from pydantic.alias_generators import to_snake

from apicaller.base import BaseAPICaller


def to_dict(obj):
    if isinstance(obj, list):
        return [to_dict(item) for item in obj]
    return obj.to_dict()


class OpenaiCaller:
    def __init__(self, caller: BaseAPICaller):
        self._caller = caller

    def call_function(self, function: Function) -> str:
        arguments = json.loads(function.arguments)
        arguments['parameters'] = {to_snake(k): v for k, v in arguments['parameters'].items()}
        response = self._caller.call_api(function.name, **arguments['parameters'])
        if response:
            return json.dumps(to_dict(response))
        return "Not found or other error"

    def get_tools(self):
        return self._caller.get_tools()
