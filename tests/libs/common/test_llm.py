import json
from types import SimpleNamespace

import pytest
from google.api_core import exceptions

from libs.common import llm as llm_module
from libs.common.llm import VertexLLM


class FakeGenerationConfig:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeResponse:
    def __init__(self, text=None):
        self.text = text


class FakeGenerativeModel:
    def __init__(self):
        self.calls = []
        self._responses = []

    def queue_response(self, response):
        self._responses.append(response)

    def generate_content(self, prompt, generation_config, timeout):
        self.calls.append(
            {
                "prompt": prompt,
                "config": generation_config,
                "timeout": timeout,
            }
        )
        if not self._responses:
            raise AssertionError("No fake response queued")
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture(autouse=True)
def configure_env(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "demo-project")
    monkeypatch.setenv("LOCATION", "europe-west4")


@pytest.fixture
def fake_model(monkeypatch):
    model = FakeGenerativeModel()

    monkeypatch.setattr(llm_module, "generative_models", SimpleNamespace())
    llm_module.generative_models.GenerationConfig = FakeGenerationConfig
    llm_module.generative_models.GenerativeModel = lambda name: model

    init_calls = []

    def fake_init(project, location):
        init_calls.append((project, location))

    monkeypatch.setattr(llm_module, "aiplatform", SimpleNamespace(init=fake_init))

    return model, init_calls


def test_generate_text_returns_model_text(fake_model):
    model, init_calls = fake_model
    model.queue_response(FakeResponse(text="Hello world"))

    client = VertexLLM()
    output = client.generate_text("Hi", temperature=0.5, max_tokens=256)

    if output != "Hello world":
        pytest.fail(f"Expected model output 'Hello world', got: {output!r}")

    if init_calls != [("demo-project", "europe-west4")]:
        pytest.fail(
            "VertexLLM initialization calls did not match expected project and location"
        )

    if not model.calls:
        pytest.fail("Fake model did not record any calls")

    call = model.calls[0]
    if call["prompt"] != ["Hi"]:
        pytest.fail(f"Expected prompt ['Hi'], got: {call['prompt']!r}")

    if not isinstance(call["config"], FakeGenerationConfig):
        pytest.fail(
            "Expected generation config to be an instance of FakeGenerationConfig"
        )

    config_kwargs = call["config"].kwargs
    if config_kwargs.get("temperature") != 0.5:
        pytest.fail("Expected generation config to use temperature=0.5")

    if config_kwargs.get("max_output_tokens") != 256:
        pytest.fail("Expected generation config to use max_output_tokens=256")


def test_generate_json_retries_on_timeout(fake_model):
    model, _ = fake_model
    model.queue_response(exceptions.DeadlineExceeded("timeout"))
    model.queue_response(FakeResponse(text=json.dumps({"status": "ok"})))

    client = VertexLLM(max_retries=2, retry_delay=0)
    payload = client.generate_json({"type": "object"}, "Prompt")

    if payload != {"status": "ok"}:
        pytest.fail(f"Expected JSON payload {{'status': 'ok'}}, got: {payload!r}")

    if len(model.calls) != 2:
        pytest.fail(
            f"Expected model to be called twice due to retry, got: {len(model.calls)}"
        )
