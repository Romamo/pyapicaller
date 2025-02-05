from apicaller.swagger import SwaggerCaller

OPENAPI_SPEC = "https://petstore3.swagger.io/api/v3/openapi.json"

swagger_caller = SwaggerCaller(OPENAPI_SPEC,
                               client_package='examples.petstore3.swagger_clients.swagger_client',
                               generate_client=True,
                               configuration={'host': 'https://petstore3.swagger.io/api/v3'})

print("Calling api directly")
pet = swagger_caller.call_api('getPetById', pet_id=5)
print(pet)
