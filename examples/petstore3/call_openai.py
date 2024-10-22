from openai import OpenAI
from apicaller import OpenaiCaller, SwaggerCaller

# Use any OpenAPI spec file
OPENAPI_SPEC = "examples/petstore3/openapi.json"
# Generate swagger client and copy the client package to the current directory
CLIENT_PACKAGE = "swagger_client"

client = OpenAI()
swagger_caller = SwaggerCaller(CLIENT_PACKAGE, OPENAPI_SPEC)
caller = OpenaiCaller(swagger_caller)


def get_openai_response(functions, messages):
    return client.chat.completions.create(
        model='gpt-4o-mini',
        tools=functions,
        tool_choice="auto",  # "auto" means the model can pick between generating a message or calling a function.
        temperature=0,
        messages=messages,
    )


functions = caller.get_functions()
messages = [
    {"role": "user", "content": "Get pet id 5"},
]

for num_calls in range(5):
    response = get_openai_response(functions, messages)
    if response.choices[0].message.tool_calls:
        messages.append(response.choices[0].message)
        messages.append({"role": "tool",
                         "content": caller.call_function(response.choices[0].message.tool_calls[0].function),
                         "tool_call_id": response.choices[0].message.tool_calls[0].id})
    else:
        print(response.choices[0].message.content)
        break
