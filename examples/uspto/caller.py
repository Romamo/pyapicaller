from apicaller.swagger import SwaggerCaller

# https://learn.openapis.org/examples/v3.0/uspto.html
swagger_caller = SwaggerCaller('examples/uspto/uspto.json',
                               client_package='examples.uspto.swagger_clients.swagger_client',
                               generate_client=True,
                               configuration={'host': "https://developer.uspto.gov/ds-api"})

print("Tools", swagger_caller.get_tools())

reponse = swagger_caller.call_api('list-data-sets')
print(reponse)
