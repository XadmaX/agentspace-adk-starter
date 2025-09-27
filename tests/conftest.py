import sys
from types import ModuleType


def ensure_module(name: str) -> ModuleType:
    module = sys.modules.get(name)
    if module is None:
        module = ModuleType(name)
        sys.modules[name] = module
    return module


# Stub jwt before modules import
jwt_module = ensure_module("jwt")
if not hasattr(jwt_module, "encode"):
    jwt_module.encode = lambda payload, key, algorithm: "signed-jwt"


# Stub google api_core exceptions used by VertexLLM and other helpers
api_core_module = ensure_module("google.api_core")
exceptions_module = ensure_module("google.api_core.exceptions")


class _GoogleError(Exception):
    pass


for exc_name in [
    "DeadlineExceeded",
    "ResourceExhausted",
    "ServiceUnavailable",
    "InternalServerError",
    "GoogleAPICallError",
]:
    if not hasattr(exceptions_module, exc_name):
        setattr(exceptions_module, exc_name, type(exc_name, (_GoogleError,), {}))

api_core_module.exceptions = exceptions_module


# Minimal google.cloud submodules referenced in code
cloud_module = ensure_module("google.cloud")
for submodule in ["aiplatform", "firestore", "pubsub_v1", "secretmanager"]:
    ensure_module(f"google.cloud.{submodule}")
    setattr(cloud_module, submodule, sys.modules[f"google.cloud.{submodule}"])


def _noop_init(*args, **kwargs):
    return None


sys.modules["google.cloud.aiplatform"].init = _noop_init


# Vertex AI generative models placeholder
vertexai_module = ensure_module("vertexai")
vertexai_generative = ensure_module("vertexai.generative_models")
vertexai_module.generative_models = vertexai_generative


# Basic requests module placeholder used for typing/imports
requests_module = ensure_module("requests")
if not hasattr(requests_module, "Session"):
    class _Session:  # pragma: no cover - only used to satisfy imports
        def __init__(self, *args, **kwargs):
            pass

        def get(self, *args, **kwargs):  # noqa: D401
            raise NotImplementedError("requests.Session stub does not support GET")

        def post(self, *args, **kwargs):  # noqa: D401
            raise NotImplementedError("requests.Session stub does not support POST")

    requests_module.Session = _Session
