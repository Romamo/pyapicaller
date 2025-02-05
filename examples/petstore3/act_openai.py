try:
    from openai import OpenAI
except ModuleNotFoundError:
    raise ModuleNotFoundError("This example requires openai package. Install it with `pip install openai`")

from apicaller.openai_caller import OpenaiCaller
from apicaller.swagger import SwaggerCaller

OPENAPI_SPEC = "https://petstore3.swagger.io/api/v3/openapi.json"

swagger_caller = SwaggerCaller(OPENAPI_SPEC,
                               client_package='examples.petstore3.swagger_clients.swagger_client',
                               generate_client=True,
                               configuration={'host': 'https://petstore3.swagger.io/api/v3'})

client = OpenAI()
caller = OpenaiCaller(swagger_caller)


def get_openai_response(tools, messages):
    return client.chat.completions.create(
        model='gpt-4o-mini',
        tools=tools,
        tool_choice="auto",  # "auto" means the model can pick between generating a message or calling a function.
        temperature=0,
        messages=messages,
    )


tools = caller.get_tools()
messages = [
    {"role": "user", "content": "Get pet id 5"},
]

for num_calls in range(5):
    response = get_openai_response(tools, messages)
    if response.choices[0].message.tool_calls:
        messages.append(response.choices[0].message)
        messages.append({"role": "tool",
                         "content": caller.call_function(response.choices[0].message.tool_calls[0].function),
                         "tool_call_id": response.choices[0].message.tool_calls[0].id})
    else:
        print(response.choices[0].message.content)
        break
