import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dataset import image_path, load_sample
from google import genai

from llm_validation_loop import run_validation_loop
from tally_sheet.extractor import GeminiExtractor, ocr_parts, vision_parts
from tally_sheet.ground_truth import parse_qr
from tally_sheet.images import load_content
from tally_sheet.ocr import OcrReader
from tally_sheet.rules import validate_tally_sheet
from tally_sheet.scoring import score_tally_sheet

MAX_ROUNDS = 3
ROOT_DIR = Path(__file__).resolve().parent.parent
TRACES_DIR = ROOT_DIR / "results" / "traces"
OCR_DIR = ROOT_DIR / "data" / "ocr"


def main():
    args = _parse_args()
    pending = [e for e in _limited(load_sample(), args.limit) if not _done(args, e)]
    sources = _prepare_sources(args.source, pending)
    client = genai.Client()

    with ThreadPoolExecutor(args.workers) as pool:
        jobs = [
            pool.submit(_run_one, client, args, e, sources[e["acta_id"]])
            for e in pending
        ]
        for job in jobs:
            print(job.result())

    print(f"✅ {len(pending)} tally sheets processed with source '{args.source}'")


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=("vision", "ocr"), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=4)

    return parser.parse_args()


def _limited(sample, limit):
    if not limit:
        return sample

    per_family = limit // 2
    high = [e for e in sample if e["family"] == "high_res"][:per_family]
    low = [e for e in sample if e["family"] == "low_res"][: limit - per_family]

    return high + low


def _trace_path(args, entry):
    return TRACES_DIR / args.source / f"{entry['acta_id']}.json"


def _done(args, entry):
    return _trace_path(args, entry).exists()


def _prepare_sources(source, entries):
    if source == "vision":
        return {e["acta_id"]: (vision_parts(_content(e)), None) for e in entries}

    reader = OcrReader()
    texts = {e["acta_id"]: _ocr_text(reader, e) for e in entries}

    return {acta_id: (ocr_parts(text), text) for acta_id, text in texts.items()}


def _ocr_text(reader, entry):
    path = OCR_DIR / f"{entry['acta_id']}.txt"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(reader.read(_content(entry)))

    return path.read_text()


def _content(entry):
    return load_content(image_path(entry["image"]))


def _run_one(client, args, entry, prepared):
    parts, source_text = prepared
    extractor = GeminiExtractor(client, args.model, args.source, parts)
    result = run_validation_loop(extractor, validate_tally_sheet, MAX_ROUNDS)
    trace = _build_trace(args, entry, result, source_text)
    path = _trace_path(args, entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(trace, indent=2, ensure_ascii=False) + "\n")

    return _progress_line(trace)


def _build_trace(args, entry, result, source_text):
    truth = parse_qr(entry["qr"])
    attempts = result.to_dict()["attempts"]

    for attempt in attempts:
        score = score_tally_sheet(attempt["output"], truth)
        attempt["score"] = {"exact": score.exact, "wrong_fields": score.wrong_fields}

    return {
        **entry,
        "source": args.source,
        "model": args.model,
        "source_text": source_text,
        "passed": result.passed,
        "attempts": attempts,
    }


def _progress_line(trace):
    marks = "".join("✓" if a["score"]["exact"] else "✗" for a in trace["attempts"])
    status = "✅" if trace["passed"] else "⚠️"

    return f"{status} {trace['acta_id']} {trace['family']:8} {marks}"


if __name__ == "__main__":
    main()
