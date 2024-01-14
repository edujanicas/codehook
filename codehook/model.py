from enum import Enum

class Events(str, Enum):
    all = "*"

class CloudName(str, Enum):
    aws = "aws"

class Cloud:
    """
    Represents a cloud service provider.

    Methods:
    - create_function: Creates a new function in the cloud.
    - update_function: Updates an existing function in the cloud.
    - delete_function: Deletes a function from the cloud.
    - list_functions: Lists all functions available in the cloud.
    - create_api: Creates a new API in the cloud.
    - delete_api: Deletes an API from the cloud.
    - list_apis: Lists all APIs available in the cloud.
    """
    def __init__(self):
        pass
    
    def create_function(self, name: str, path: str):
        pass

    def update_function(self, id: str, path: str):
        pass

    def delete_function(self, id: str):
        pass

    def list_functions(self):
        pass

    def create_api(self, name: str, function_id: str):
        pass

    def delete_api(self, id: str):
        pass

    def list_apis(self):
        pass


class SourceName(str, Enum):
    stripe = "stripe"

class Source():
    """
    Represents a source of webhook events.

    Methods:
    - create_webhook: Creates a new webhook endpoint in the source.
    - delete_webhook: Deletes a webhook endpoint from the source.
    - list_webhooks: Lists all webhook endpoints available in the source.
    """
    def __init__(self):
        pass
    
    def create_webhook(self, events: list[Events], url: str):
        pass

    def delete_webhook(self, id: str):
        pass

    def list_webhooks(self):
        pass



