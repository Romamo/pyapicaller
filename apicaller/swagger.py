import importlib
import re
import urllib.request
from typing import Union

import jsonref
import yaml
from pydantic.alias_generators import to_snake, to_pascal

from .base import BaseAPICaller


class SwaggerCaller(BaseAPICaller):
    _spec = None
    _openapi = None
    _configuration = None
    _client = None

    def __init__(self, swagger_client: str, openapi: Union[str, dict] = None, configuration: dict = None):
        self.client_package = swagger_client
        if openapi:
            if isinstance(openapi, dict):
                self._spec = openapi
            else:
                self._openapi = openapi

        if configuration:
            self._configuration = configuration

    def _load_yaml(self, content: str):
        self._spec = yaml.safe_load(content)

    def _load_json(self, content: str):
        self._spec = jsonref.loads(content)

    def _load_spec(self):
        if self._openapi.startswith('http'):
            response = urllib.request.urlopen(self._openapi)
            content = response.read()
        else:
            with open(self._openapi, 'br') as f:
                content = f.read()

        if content.startswith(b'{'):
            self._load_json(content)
        else:
            self._load_yaml(content)

        # resolve references
        self._spec = jsonref.replace_refs(self._spec)

    def _get_module(self, module_name: str = None):
        if module_name:
            full_module_name = f"{self.client_package}.{module_name}"
        else:
            full_module_name = self.client_package
        try:
            return importlib.import_module(full_module_name)
        except ModuleNotFoundError:
            raise ValueError(f"Not found module {full_module_name}")

    def _get_api_module(self, module_name: str):
        """Dynamically import and return an API module equivalent to

        from spotify_swagger_client.api import pet_api
        """
        return self._get_module(f"api.{module_name}_api")

    def _get_module_attr(self, attr: str):
        module = self._get_module()
        return getattr(module, attr)

    def _configure(self):
        if self._configuration:
            configuration_class = self._get_module_attr('Configuration')

            configuration = configuration_class()

            for k, v in self._configuration.items():
                setattr(configuration, k, v)
            return configuration

    def _create_client(self):
        if not self._client:
            api_client_class = self._get_module_attr('ApiClient')

            self._client = api_client_class(self._configure())
        return self._client

    def _create_api(self, module_name: str):
        """Dynamically create an API instance from a module."""
        api_module = self._get_api_module(module_name)

        # Get the API class from the module
        api_class = getattr(api_module, f"{to_pascal(module_name)}Api", None)
        if not api_class:
            raise ValueError(f"API class '{to_pascal(module_name)}Api' not found'")
        return api_class(self._create_client())

    def get_method(self, operation_id: str) -> callable:
        if not self._spec:
            self._load_spec()
        for path, methods in self._spec["paths"].items():
            for method, spec in methods.items():
                if spec.get('operationId') == operation_id:
                    path = re.sub(r"({.+})", '', path)
                    path = path.strip('/')
                    if '/' in path:
                        path = path.split('/')[0]

                    api = self._create_api(path)
                    return getattr(api, to_snake(spec.get('operationId')))

    def call_api(self, operation_id: str, *args, **kwargs):
        method = self.get_method(operation_id)

        self._configure()

        try:
            response = method(*args, **kwargs)
        except Exception as e:
            print(e)
            if e.status == 404:
                return None
            return
        return response

    def get_functions(self) -> list[dict]:
        if not self._spec:
            self._load_spec()

        functions = []

        for path, methods in self._spec["paths"].items():
            for method, spec in methods.items():

                function_name = spec.get('operationId')

                # 3. Extract a description and parameters.
                desc = spec.get("description") or spec.get("summary", "")

                schema = {"type": "object", "properties": {}}

                req_body = (
                    spec.get("requestBody", {})
                    .get("content", {})
                    .get("application/json", {})
                    .get("schema")
                )
                if req_body:
                    schema["properties"]["requestBody"] = req_body

                params = spec.get("parameters", [])
                if params:
                    param_properties = {
                        param["name"]: param["schema"]
                        for param in params
                        if "schema" in param
                    }
                    schema["properties"]["parameters"] = {
                        "type": "object",
                        "properties": param_properties,
                    }

                functions.append(
                    {"type": "function", "function": {"name": function_name, "description": desc, "parameters": schema}}
                )

        return functions
