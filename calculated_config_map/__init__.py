import _jsonnet  # type: ignore
import datetime
import json
import kopf
import kubernetes  # type: ignore
import logging

from .k8s import configmap as k8s_configmap
from .k8s import namespace as k8s_namespace
from .kopflib import events


def parse_context(body: kopf.Body) -> tuple[dict[str, str], dict[str, str]]:
    # generate ext_vars and tlas
    args: dict[str, str] = {}
    tlas: dict[str, str] = {}
    for n, defn in body["spec"]["context"].items():
        tp = defn.get("type", "string")
        value = None
        if "arg" in defn:
            target = args
            value = defn["arg"]
        elif "var" in defn:
            target = tlas
            value = defn["value"]
        if tp == "string":
            value = json.dumps(value)
        target[n] = value or "null"
    return args, tlas


@kopf.on.create("k8s.haeger.de", "calculatedconfigmap")  # type: ignore
@kopf.on.update("k8s.haeger.de", "calculatedconfigmap")  # type: ignore
@kopf.on.resume("k8s.haeger.de", "calculatedconfigmap")  # type: ignore
def sync(name: str, namespace: str, body: kopf.Body, logger, **_):
    with kubernetes.client.ApiClient() as client:
        ns_api = k8s_namespace.NamespaceApi(client)
        if ns_api.is_terminating(namespace):
            return {}

    last_synchronized = body.get("status", {}).get("sync", {}).get("lastSynchronized")

    tlas, ext_vars = parse_context(body)

    try:
        values = json.loads(
            _jsonnet.evaluate_snippet(
                f"{namespace}:{name}",
                body["spec"]["template"]["jsonnet"],
                ext_codes=ext_vars,
                tla_codes=tlas,
            )
        )
    except RuntimeError as ex:
         # events.error(body, reason="TemplateFailed", message=f"Template error: {ex}")
        raise kopf.PermanentError(str(ex))

    configmap_resource = k8s_configmap.ConfigMapResource.template(
        name=name,
        namespace=namespace,
        values={k: v if isinstance(v, str) else json.dumps(v) for k, v in values.items()},
    )
    kopf.adopt(configmap_resource)

    with kubernetes.client.ApiClient() as client:
        configmap_api = k8s_configmap.ConfigMapApi(client)
        changed = configmap_api.sync(configmap_resource)

    if changed or not last_synchronized:
        # events.info(body, reason="Sync", message="ConfigMap updated")
        last_synchronized = datetime.datetime.utcnow().isoformat()

    return {"lastSynchronized": last_synchronized}


@kopf.on.startup()
async def start(settings: kopf.OperatorSettings, **_):
    #settings.posting.level = logging.CRITICAL
    pass


@kopf.on.login()
async def login(**kwargs):
    global operator_namespace
    try:
        kubernetes.config.load_incluster_config()
    except kubernetes.config.config_exception.ConfigException:
        kubernetes.config.load_kube_config()
    return kopf.login_via_client(**kwargs)
