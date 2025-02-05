from apicaller.swagger import SwaggerCaller

# Use any OpenAPI spec file
OPENAPI_SPEC = 'https://raw.githubusercontent.com/sonallux/spotify-web-api/refs/heads/main/official-spotify-open-api.yml'
# Get access token https://developer.spotify.com/documentation/web-api
ACCESS_TOKEN = 'ACCESS_TOKEN'

swagger_caller = SwaggerCaller(OPENAPI_SPEC,
                               client_package='examples.spotify.swagger_clients.swagger_client',
                               generate_client=True,
                               configuration={'access_token': ACCESS_TOKEN})

album = swagger_caller.call_api('get-an-album', id='xxx')
print(album)
