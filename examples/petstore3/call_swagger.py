from apicaller.swagger import SwaggerCaller

# Use any OpenAPI spec file
OPENAPI_SPEC = "examples/petstore3/openapi.json"
# Generate swagger client and copy the client package to the current directory
CLIENT_PACKAGE = "swagger_client"

swagger_caller = SwaggerCaller(CLIENT_PACKAGE, OPENAPI_SPEC)
pet = swagger_caller.call_api('getPetById', pet_id=5)
print(pet)
