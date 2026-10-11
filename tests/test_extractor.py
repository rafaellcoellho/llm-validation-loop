from types import SimpleNamespace

from llm_validation_loop import Attempt, Violation
from tally_sheet.extractor import GeminiExtractor


def fake_response(text):
    usage = SimpleNamespace(
        prompt_token_count=1000, candidates_token_count=200, thoughts_token_count=None
    )

    return SimpleNamespace(text=text, usage_metadata=usage)


class FakeClient:
    def __init__(self, text):
        self.calls = []
        self.models = SimpleNamespace(generate_content=self._generate)
        self._text = text

    def _generate(self, model, contents, config):
        self.calls.append(contents)

        return fake_response(self._text)


def extractor_for(client):
    return GeminiExtractor(client, "some-model", "ocr", source_parts=[])


def test_first_round_sends_only_the_source_and_prompt():
    client = FakeClient('{"a": 1}')

    extraction = extractor_for(client)([])

    assert extraction.output == {"a": 1}
    assert [content.role for content in client.calls[0]] == ["user"]


def test_later_rounds_replay_each_answer_and_its_feedback():
    client = FakeClient("{}")
    failed = Attempt(1, {"a": 1}, [Violation("party_sum", "off by 10")])

    extractor_for(client)([failed])

    roles = [content.role for content in client.calls[0]]
    feedback = client.calls[0][2].parts[0].text
    assert roles == ["user", "model", "user"]
    assert client.calls[0][1].parts[0].text == '{"a": 1}'
    assert "[party_sum] off by 10" in feedback


def test_keeps_unparsable_text_for_the_validator():
    extraction = extractor_for(FakeClient("not json"))([])

    assert extraction.output == {"unparsable_response": "not json"}


def test_reports_token_usage():
    extraction = extractor_for(FakeClient("{}"))([])

    assert extraction.usage == {
        "input_tokens": 1000,
        "output_tokens": 200,
        "thinking_tokens": 0,
    }
