from typing import Dict, Any


def _get_type(schema: Dict[str, Any]) -> str:
    type_mapping = {
        "integer": "int",
        "string": "str",
        "boolean": "bool",
        "number": "float",
        "object": "object",
        "array": "list",
    }
    schema_type = schema.get("type", "object")
    if schema_type not in type_mapping:
        raise ValueError(f"Unsupported schema type {schema_type}")
    return type_mapping[schema_type]


def _parse_schema(
    schema: Dict[str, Any], required: bool, description: str
) -> Dict[str, Any]:
    schema_type = _get_type(schema)
    if schema_type == "object":
        properties = schema.get("properties", {})
        nested_parameters = {
            name: _parse_schema(
                schema=prop_schema,
                required=bool(name in schema.get("required", [])),
                description=prop_schema.get("description", ""),
            )
            for name, prop_schema in properties.items()
        }
        return {
            "type": schema_type,
            "description": description,
            "properties": nested_parameters,
            "required": required,
        }
    return {"type": schema_type, "description": description, "required": required}


def _parse_parameters(operation: Dict[str, Any]) -> Dict[str, Any]:
    parameters = {}
    for param in operation.get("parameters", []):
        if "schema" in param:
            parameters[param["name"]] = _parse_schema(
                param["schema"],
                param.get("required", False),
                param.get("description", ""),
            )
    if "requestBody" in operation:
        content = (
            operation["requestBody"].get("content", {}).get("application/json", {})
        )
        if "schema" in content:
            schema_properties = content["schema"].get("properties", {})
            required_properties = content["schema"].get("required", [])
            for name, schema in schema_properties.items():
                parameters[name] = _parse_schema(
                    schema, name in required_properties, schema.get("description", "")
                )
    return parameters
