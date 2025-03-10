import kubernetes  # type: ignore


class ConfigMapResource:
    K8SGroup = ""
    K8SVersion = "v1"
    K8SKind = "ConfigMap"
    K8SPluralName = "configmaps"

    @classmethod
    def template(cls, name: str, namespace: str, values: dict[str, str]) -> dict:
        return {
            "apiVersion": f"{cls.K8SGroup}{cls.K8SVersion}",
            "kind": cls.K8SKind,
            "metadata": {
                "name": name,
                "namespace": namespace,
            },
            "data": values,
        }


class ConfigMapApi:
    def __init__(self, client: kubernetes.client.ApiClient):
        self._api = kubernetes.client.CoreV1Api(client)

    def get(self, namespace: str, name: str) -> dict | None:
        try:
            return self._api.read_namespaced_config_map(name, namespace)
        except kubernetes.client.ApiException as ex:
            if ex.status == 404:
                return None
            raise

    def create(self, body: dict) -> None:
        namespace = body.get("metadata", {}).get("namespace")
        self._api.create_namespaced_config_map(namespace, body)

    def patch(self, body: dict) -> None:
        name = body.get("metadata", {}).get("name")
        namespace = body.get("metadata", {}).get("namespace")
        self._api.patch_namespaced_config_map(name, namespace, body)

    def sync(self, body: dict) -> bool:
        existing = self.get(
            body.get("metadata", {}).get("namespace"), body.get("metadata", {}).get("name")
        )
        if not existing:
            self.create(body)
            return True
        elif existing.data != body.data:
            self.patch(body)
            return True
        return False
