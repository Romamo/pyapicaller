# API Caller

[![GitHub license](https://img.shields.io/github/license/Romamo/pyapicaller)](

Easily connect any API to OpenAI function calling.

## Description

With the introduction of OpenAI's function calling, a new era of AI-powered API interaction has begun. This project aims to provide a simple and effective way to connect any API to OpenAI function calling.

The current version supports OpenAPI specifications and generated Swagger clients. Additional API specifications will be supported in future releases.

For more inspiration, check out the original post that influenced this project: [Function calling with an OpenAPI specification](https://cookbook.openai.com/examples/function_calling_with_an_openapi_spec)

## Prerequisites

To use this project, you need to have a generated Swagger Python client. 
You can generate this client from your OpenAPI specification with
[Swagger Codegen](https://github.com/swagger-api/swagger-codegen) or [Swagger Editor](https://editor.swagger.io/).

Requires Python 3.9+

## Install
Ascetic with OpenAPI and Tools validation 
```bash
pip install pyapicaller
```
With swagger support
```bash
pip install pyapicaller[swagger]
```
With all options
```bash
pip install pyapicaller[yaml,swagger,openai]
```
## Usage

Use operationId and generated swagger client to call the API. Swagger client will be autogenerated.

```python
from apicaller.swagger import SwaggerCaller

# Use any OpenAPI spec file
OPENAPI_SPEC = "https://petstore3.swagger.io/api/v3/openapi.json"

swagger_caller = SwaggerCaller(OPENAPI_SPEC,
                               client_package='examples.petstore3.swagger_clients.swagger_client',
                               generate_client=True,
                               configuration={'host': 'https://petstore3.swagger.io/api/v3'})

pet = swagger_caller.call_api('getPetById', pet_id=5)
print(pet)
```
Use OpenAI to really call API
```python
from openai import OpenAI
from apicaller import OpenaiCaller, SwaggerCaller

# Use any OpenAPI spec file
OPENAPI_SPEC = "https://petstore3.swagger.io/api/v3/openapi.json"

swagger_caller = SwaggerCaller(OPENAPI_SPEC,
                               client_package='examples.petstore3.swagger_clients.swagger_client',
                               generate_client=True,
                               configuration={'host': 'https://petstore3.swagger.io/api/v3'})
caller = OpenaiCaller(swagger_caller)
client = OpenAI()


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

        # Call the API(magic) 
        content = caller.call_function(response.choices[0].message.tool_calls[0].function)
        
        messages.append({"role": "tool",
                         "content": content,
                         "tool_call_id": response.choices[0].message.tool_calls[0].id})
    else:
        print(response.choices[0].message.content)
        break

```

```text
The details for pet ID 5 are as follows:

- **Name:** doggie
- **Category:** Dogs
- **Photo URLs:** ["string"]
- **Tags:** [{"id": 0, "name": "string"}]
- **Status:** available
```
