import http.client
import importlib
import inspect
import io
import json
import os
import re
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Union

import jsonref

from .base import BaseAPICaller


class SwaggerCaller(BaseAPICaller):
    _spec = None
    _openapi = None
    _client = None
    _map = None
    _apis = None

    def __init__(self, openapi: Union[str, dict] = None,
                 client_package: Union[Path, str] = 'swagger_clients.swagger_client',
                 generate_client: bool = False,
                 configuration: dict = None
                 ):
        if openapi:
            if isinstance(openapi, dict):
                self._spec = openapi
            else:
                self._openapi = openapi

        if client_package:
            self._client_package = client_package
        self._configuration = configuration
        self._generate_client = generate_client

    def _get_path(self):
        return self._client_package.rsplit('.', 1)[0].replace('.', '/')

    def generate(self):
        # Path append
        if not os.path.exists(self._get_path()):
            if not self._spec:
                self._load_spec()

            # Call swagger generator API to generate the client
            conn = http.client.HTTPSConnection('generator3.swagger.io')
            conn.request('POST', '/api/generate',
                         json.dumps({
                             "spec": json.loads(jsonref.dumps(self._spec)),
                             "type": "CLIENT",
                             "lang": "python"
                         }),
                         {'Content-type': 'application/json'})
            response = conn.getresponse()
            if response.status == 200:
                # Create a ZipFile object from the response content
                zip_file = zipfile.ZipFile(io.BytesIO(response.read()))
                # Extract the contents of the zip file
                zip_file.extractall(self._get_path())
                importlib.invalidate_caches()

                return True
            else:
                raise Exception("Cannot download generated client")

    def validate(self):
        try:
            from openapi_spec_validator import validate
        except ImportError as e:
            raise ImportError("`openapi-spec-validator` not installed. Please install using "
                              "`pip install openapi-spec-validator`")

        if not self._spec:
            self._load_spec()

        response = validate(self._spec)
        return response

    def _load_yaml(self, content: str):
        try:
            import yaml
        except ImportError:
            raise ImportError("Required yaml package. Install it with `pip install pyyaml`")
        self._spec = yaml.safe_load(content)

    def _load_json(self, content: str):
        try:
            import jsonref
        except ImportError:
            raise ImportError("Required jsonref package. Install it with `pip install jsonref`")
        self._spec = jsonref.loads(content)  # , proxies=False
        self._spec = jsonref.replace_refs(self._spec)

    def _read_spec(self):
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

    @staticmethod
    def _to_key(operation_id: str):
        return re.sub(r'[-_:.]', '', operation_id).lower()

    def _create_map(self):
        self._map = {}
        self._apis = {}
        methods = {}
        module = self._get_module()
        api_module_prefix = f"{self._client_package.rsplit('.', 1)[-1]}.api."
        for name, type_ in inspect.getmembers(module, inspect.isclass):
            if type_.__module__.startswith(api_module_prefix):
                api_name = type_.__module__.rsplit('.', 1)[-1].replace('_api', '')
                self._apis[api_name] = name

                for name_func, type_func in inspect.getmembers(type_, inspect.isfunction):
                    if name_func != '__init__' and not name_func.endswith('_with_http_info'):
                        method_name = name_func.replace('_', '').lower()
                        methods[method_name] = api_name, type_func.__name__

        for path, path_item in self._spec['paths'].items():
            for method, operation in path_item.items():
                operation_id = self._to_key(operation.get('operationId'))
                if operation_id in methods:
                    self._map[operation_id] = methods[operation_id]
                else:
                    print(f"Warning: operationId {operation_id} not found in generated client")

    def _load_spec(self):
        self._read_spec()

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

    def _get_api_module_name(self, path):
        path = re.sub(r"({.+})", '', path)
        path = path.strip('/')
        if '/' in path:
            path = path.split('/')[0]
        return path

    def _get_module(self, module_name: str = None):
        if self._get_path() not in sys.path:
            sys.path.insert(0, self._get_path())

        full_module_name = self._client_package
        if module_name:
            full_module_name += '.' + module_name
        try:
            return importlib.import_module(full_module_name)
        except ModuleNotFoundError:
            if module_name is None and self._generate_client:
                self.generate()
                return importlib.import_module(full_module_name)
            raise ValueError(f"Not found module {full_module_name}")

    def _get_api_module(self, module_name: str):
        """Dynamically import and return an API module equivalent to

        from spotify_swagger_client.api import pet_api
        """
        return self._get_module(f"api.{module_name}_api")

    def _create_api(self, module_name: str):
        """Dynamically create an API instance from a module."""
        api_module = self._get_api_module(module_name)

        # Get the API class from the module
        api_class = getattr(api_module, self._apis[module_name], None)
        if not api_class:
            raise ValueError(f"API class '{self._apis[module_name]}' not found'")
        return api_class(self._create_client())

    def get_method(self, operation_id: str) -> callable:
        if not self._spec:
            self._load_spec()
        if not self._map:
            self._create_map()

        api_module, method = self._map[self._to_key(operation_id)]

        api = self._create_api(api_module)

        return getattr(api, method)

    def call_api(self, operation_id: str, *args, **kwargs):
        method = self.get_method(operation_id)

        self._configure()

        response = method(*args, **kwargs)
        # try:
        #     response = method(*args, **kwargs)
        # except Exception as e:
        #     print(e)
        #     if e.status == 404:
        #         return None
        #     return
        return response

    def get_tools(self) -> list[dict]:
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
