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

    assert output == "Hello world"
    assert init_calls == [("demo-project", "europe-west4")]

    call = model.calls[0]
    assert call["prompt"] == ["Hi"]
    assert isinstance(call["config"], FakeGenerationConfig)
    assert call["config"].kwargs["temperature"] == 0.5
    assert call["config"].kwargs["max_output_tokens"] == 256


def test_generate_json_retries_on_timeout(fake_model):
    model, _ = fake_model
    model.queue_response(exceptions.DeadlineExceeded("timeout"))
    model.queue_response(FakeResponse(text=json.dumps({"status": "ok"})))

    client = VertexLLM(max_retries=2, retry_delay=0)
    payload = client.generate_json({"type": "object"}, "Prompt")

    assert payload == {"status": "ok"}
    assert len(model.calls) == 2
