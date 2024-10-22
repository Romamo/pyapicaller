import importlib
import re
from typing import Union
import urllib.request

import jsonref
from pydantic.alias_generators import to_snake, to_pascal

from .base import BaseAPICaller


class SwaggerCaller(BaseAPICaller):
    _spec = None
    _openapi = None

    def __init__(self, swagger_client: str, openapi: Union[str, dict] = None):
        self.client_package = swagger_client
        if openapi:
            if isinstance(openapi, dict):
                self._spec = openapi
            else:
                self._openapi = openapi

    def _load_spec(self):
        if self._openapi.startswith('http'):
            response = urllib.request.urlopen(self._openapi)
            content = response.read()
        else:
            with open(self._openapi, 'r') as f:
                content = f.read()
        self._spec = jsonref.loads(content)

    def _get_api_module(self, module_name: str):
        """Dynamically import and return an API module equivalent to

        from swagger_client.api import pet_api
        """
        full_module_name = f"{self.client_package}.api.{module_name}_api"
        try:
            return importlib.import_module(full_module_name)
        except ModuleNotFoundError:
            raise ValueError(f"Not found API module {full_module_name}")

    def _create_api(self, module_name: str):
        """Dynamically create an API instance from a module."""
        api_module = self._get_api_module(module_name)

        # Get the API class from the module
        api_class = getattr(api_module, f"{to_pascal(module_name)}Api", None)
        if not api_class:
            raise ValueError(f"API class '{to_pascal(module_name)}Api' not found'")
        return api_class()

    def get_method(self, operation_id: str) -> callable:
        if not self._spec:
            self._load_spec()
        for path, methods in self._spec['paths'].items():
            for method, spec_with_ref in methods.items():
                spec = jsonref.replace_refs(spec_with_ref)
                if spec.get('operationId') == operation_id:
                    path = re.sub(r"({.+})", '', path)
                    path = path.strip('/')
                    if '/' in path:
                        path = path.split('/')[0]

                    api = self._create_api(path)
                    return getattr(api, to_snake(spec.get('operationId')))

    def call_api(self, operation_id: str, *args, **kwargs):
        method = self.get_method(operation_id)

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
            for method, spec_with_ref in methods.items():
                # 1. Resolve JSON references.
                spec = jsonref.replace_refs(spec_with_ref)

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
