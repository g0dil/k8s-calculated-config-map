import kopf
import logging
import kubernetes  # type: ignore

logger = logging.getLogger(__name__)


@kopf.on.startup()
async def start(settings: kopf.OperatorSettings, memo: kopf.Memo, **_):
    settings.posting.level = logging.CRITICAL


@kopf.on.login()
async def login(**kwargs):
    global operator_namespace
    try:
        kubernetes.config.load_incluster_config()
    except kubernetes.config.config_exception.ConfigException:
        kubernetes.config.load_kube_config()
    return kopf.login_via_client(**kwargs)
