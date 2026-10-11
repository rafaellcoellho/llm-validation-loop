import json
import time

from google.genai import errors, types

from llm_validation_loop import Extraction, build_feedback
from tally_sheet.images import split_vertically, to_jpeg_bytes
from tally_sheet.prompt import build_prompt
from tally_sheet.schema import TallySheet

API_RETRIES = 4


class GeminiExtractor:
    def __init__(self, client, model, source, source_parts):
        self._client = client
        self._model = model
        self._opening = [*source_parts, types.Part.from_text(text=build_prompt(source))]
        self._config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TallySheet,
        )

    def __call__(self, history):
        response = self._generate(self._conversation(history))

        return Extraction(_parse_json(response.text), _usage_of(response))

    def _conversation(self, history):
        contents = [types.Content(role="user", parts=self._opening)]

        for attempt in history:
            answer = json.dumps(attempt.output, ensure_ascii=False)
            contents.append(_message("model", answer))
            contents.append(_message("user", build_feedback(attempt)))

        return contents

    def _generate(self, contents):
        for wait in _backoff():
            try:
                return self._client.models.generate_content(
                    model=self._model, contents=contents, config=self._config
                )
            except errors.APIError as error:
                if error.code not in (429, 500, 503):
                    raise
                time.sleep(wait)

        raise RuntimeError(f"Gemini API kept failing after {API_RETRIES} retries")


def vision_parts(content_image):
    return [
        types.Part.from_bytes(data=to_jpeg_bytes(segment), mime_type="image/jpeg")
        for segment in split_vertically(content_image)
    ]


def ocr_parts(ocr_text):
    return [types.Part.from_text(text=ocr_text)]


def _message(role, text):
    return types.Content(role=role, parts=[types.Part.from_text(text=text)])


def _backoff():
    return [2**attempt * 5 for attempt in range(API_RETRIES)]


def _parse_json(text):
    try:
        return json.loads(text or "")
    except json.JSONDecodeError:
        return {"unparsable_response": text}


def _usage_of(response):
    usage = response.usage_metadata

    return {
        "input_tokens": usage.prompt_token_count or 0,
        "output_tokens": usage.candidates_token_count or 0,
        "thinking_tokens": usage.thoughts_token_count or 0,
    }
