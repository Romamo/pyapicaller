# API Caller

[![GitHub license](https://img.shields.io/github/license/Romamo/pyapicaller)](

Easily connect any API to OpenAI function calling.

## Description

With the introduction of OpenAI's function calling, a new era of AI-powered API interaction has begun. This project aims to provide a simple and effective way to connect any API to OpenAI function calling.

The current version supports OpenAPI specifications and generated Swagger clients. Additional API specifications will be supported in future releases.

## Before you start

To use this project, you need to have a generated Swagger Python client. 
You can generate this client from your OpenAPI specification using tools like:
[Swagger Codegen](https://github.com/swagger-api/swagger-codegen) or [Swagger Editor](https://editor.swagger.io/) .

For more inspiration, check out the original post that influenced this project: [Function calling with an OpenAPI specification](https://cookbook.openai.com/examples/function_calling_with_an_openapi_spec)

## Install

Requires Python 3.10+

```bash
pip install git+https://github.com/Romamo/pyapicaller.git
```

## Usage

Use operationId and generated swagger to call the API. I already added petstore swagger client to the examples folder.

```python
from apicaller.swagger import SwaggerCaller

# Use any OpenAPI spec file
OPENAPI_SPEC = "examples/petstore3/openapi.json"
# Generate swagger client and copy the client package to the current directory
CLIENT_PACKAGE = "swagger_client"

swagger_caller = SwaggerCaller(CLIENT_PACKAGE, OPENAPI_SPEC)
pet = swagger_caller.call_api('getPetById', pet_id=5)
print(pet)
```
Use OpenAI to really call API
```python
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