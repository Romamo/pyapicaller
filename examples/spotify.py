from apicaller.swagger import SwaggerCaller

# Use any OpenAPI spec file
OPENAPI_SPEC = 'https://raw.githubusercontent.com/sonallux/spotify-web-api/refs/heads/main/official-spotify-open-api.yml'
# Generate swagger client and copy the client package to the current directory
CLIENT_PACKAGE = 'swagger_client'
# Get access token https://developer.spotify.com/documentation/web-api
ACCESS_TOKEN = 'ACCESS_TOKEN'

swagger_caller = SwaggerCaller(CLIENT_PACKAGE, OPENAPI_SPEC, configuration={'debug': True, 'access_token': ACCESS_TOKEN})
# functions = swagger_caller.get_functions()
# print(functions)
album = swagger_caller.call_api('get-an-album', id='xxx')
print(album)
