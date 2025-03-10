import kubernetes  # type: ignore


class NamespaceApi:

    def __init__(self, client: kubernetes.client.ApiClient):
        self._api = kubernetes.client.CoreV1Api(client)

    def get(self, namespace: str):
        return self._api.read_namespace(namespace)

    def is_terminating(self, namespace: str):
        return self.get(namespace).status.phase == "Terminating"
