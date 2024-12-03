class BaseAPICaller:
    def get_tools(self) -> list[dict]:
        """
        Returns a list of tools formatted for OpenAI.

        :return: A list of tools that can be called.
        """
        raise NotImplementedError

    def call_api(self, operation_id: str, *args, **kwargs):
        """
        Calls the API method that corresponds to the operation_id.

        :param operation_id: Operation ID declared in the OpenAPI spec.
        :return: The response from the API call.
        """
        raise NotImplementedError

    def get_method(self, operation_id: str) -> callable:
        """
        Returns the method that corresponds to the operation_id.

        :param operation_id: Operation ID declared in the OpenAPI spec.
        :return: The method that corresponds to the operation_id.
        """
        raise NotImplementedError
