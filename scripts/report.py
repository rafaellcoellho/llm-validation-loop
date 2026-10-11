import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt

ROOT_DIR = Path(__file__).resolve().parent.parent
TRACES_DIR = ROOT_DIR / "results" / "traces"
FIGURES_DIR = ROOT_DIR / "results" / "figures"
SUMMARY_PATH = ROOT_DIR / "results" / "summary.json"

PRICE_PER_MILLION = {"input": 0.30, "output": 2.50}
GROUPS = (("vision", "high_res"), ("vision", "low_res"))
GROUPS += (("ocr", "high_res"), ("ocr", "low_res"))
GROUP_LABELS = {
    ("vision", "high_res"): "Vision\nhigh res",
    ("vision", "low_res"): "Vision\nlow res",
    ("ocr", "high_res"): "OCR → text\nhigh res",
    ("ocr", "low_res"): "OCR → text\nlow res",
}
OUTCOMES = (
    ("right_first_try", "Right on the first try"),
    ("fixed_by_loop", "Fixed by the loop"),
    ("wrong_flagged", "Wrong, flagged by the checks"),
    ("wrong_unflagged", "Wrong, passed every check"),
)
THEMES = {
    "light": {
        "surface": "#ffffff",
        "text": "#1f2328",
        "muted": "#59636e",
        "grid": "#e6e8eb",
        "series": ("#2a78d6", "#eb6834", "#1baf7a", "#eda100"),
    },
    "dark": {
        "surface": "#0d1117",
        "text": "#e6edf3",
        "muted": "#9198a1",
        "grid": "#262c36",
        "series": ("#3987e5", "#d95926", "#199e70", "#c98500"),
    },
}


def main():
    traces = _load_traces()
    summary = {f"{s}/{f}": _summarize(traces[(s, f)]) for s, f in GROUPS}
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    for theme in THEMES:
        _plot_accuracy(summary, theme)
        _plot_outcomes(summary, theme)

    print(f"✅ summary and figures written to {SUMMARY_PATH.parent}")


def _load_traces():
    traces = {group: [] for group in GROUPS}

    for path in sorted(TRACES_DIR.glob("*/*.json")):
        trace = json.loads(path.read_text())
        traces[(trace["source"], trace["family"])].append(trace)

    return traces


def _summarize(traces):
    outcomes = Counter(_outcome_of(trace) for trace in traces)
    total = len(traces)

    return {
        "tally_sheets": total,
        "exact_first_round": _share(traces, lambda t: _exact(t["attempts"][0])),
        "exact_final": _share(traces, lambda t: _exact(t["attempts"][-1])),
        "made_worse_by_loop": sum(1 for t in traces if _made_worse(t)),
        "outcomes": {key: outcomes[key] for key, _ in OUTCOMES},
        "rounds": dict(sorted(Counter(len(t["attempts"]) for t in traces).items())),
        "cost_usd": round(sum(_cost(t) for t in traces), 4),
    }


def _exact(attempt):
    return attempt["score"]["exact"]


def _share(traces, predicate):
    return round(sum(1 for t in traces if predicate(t)) / max(len(traces), 1), 4)


def _outcome_of(trace):
    first, final = trace["attempts"][0], trace["attempts"][-1]
    if _exact(first):
        return "right_first_try"
    if _exact(final):
        return "fixed_by_loop"

    return "wrong_unflagged" if trace["passed"] else "wrong_flagged"


def _made_worse(trace):
    return _exact(trace["attempts"][0]) and not _exact(trace["attempts"][-1])


def _cost(trace):
    total = 0.0

    for attempt in trace["attempts"]:
        usage = attempt["usage"]
        output = usage["output_tokens"] + usage["thinking_tokens"]
        total += usage["input_tokens"] * PRICE_PER_MILLION["input"] / 1e6
        total += output * PRICE_PER_MILLION["output"] / 1e6

    return total


def _styled_axes(theme, size):
    colors = THEMES[theme]
    figure, axes = plt.subplots(figsize=size, dpi=200)
    figure.patch.set_facecolor(colors["surface"])
    axes.set_facecolor(colors["surface"])
    axes.tick_params(colors=colors["muted"], length=0, labelsize=9)

    for side in ("top", "right", "left", "bottom"):
        axes.spines[side].set_visible(False)

    return figure, axes, colors


def _plot_accuracy(summary, theme):
    figure, axes, colors = _styled_axes(theme, (8, 3.6))
    keys = [f"{s}/{f}" for s, f in GROUPS]
    positions = range(len(keys))
    series = (("exact_first_round", "One pass"), ("exact_final", "With the loop"))

    for offset, (field, label) in zip((-0.19, 0.19), series):
        values = [summary[key][field] * 100 for key in keys]
        color = colors["series"][0 if field == "exact_first_round" else 1]
        bars = axes.bar(
            [p + offset for p in positions],
            values,
            0.36,
            color=color,
            edgecolor=colors["surface"],
            linewidth=1.5,
        )
        _label_bars(axes, bars, colors, label)

    _finish_accuracy_axes(axes, colors, keys)
    _save(figure, "accuracy", theme)


def _label_bars(axes, bars, colors, label):
    bars.set_label(label)

    for bar in bars:
        axes.annotate(
            f"{bar.get_height():.0f}%",
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color=colors["text"],
        )


def _finish_accuracy_axes(axes, colors, keys):
    axes.set_xticks(range(len(keys)))
    axes.set_xticklabels([GROUP_LABELS[tuple(k.split("/"))] for k in keys])
    axes.set_ylim(0, 112)
    axes.set_yticks([0, 25, 50, 75, 100])
    axes.yaxis.grid(True, color=colors["grid"], linewidth=0.8)
    axes.set_axisbelow(True)
    axes.set_ylabel("Tally sheets fully right (%)", color=colors["muted"], fontsize=9)
    _legend(axes, colors, ncol=2)


def _plot_outcomes(summary, theme):
    figure, axes, colors = _styled_axes(theme, (8, 3.2))
    keys = [f"{s}/{f}" for s, f in GROUPS][::-1]
    lefts = [0.0] * len(keys)

    for index, (outcome, label) in enumerate(OUTCOMES):
        widths = [_outcome_share(summary[key], outcome) for key in keys]
        bars = axes.barh(
            keys,
            widths,
            left=lefts,
            color=colors["series"][index],
            edgecolor=colors["surface"],
            linewidth=1.5,
        )
        bars.set_label(label)
        _label_segments(axes, bars, colors)
        lefts = [left + width for left, width in zip(lefts, widths)]

    _finish_outcome_axes(axes, colors, keys)
    _save(figure, "outcomes", theme)


def _outcome_share(group, outcome):
    return group["outcomes"][outcome] / max(group["tally_sheets"], 1) * 100


def _label_segments(axes, bars, colors):
    for bar in bars:
        if bar.get_width() < 6:
            continue
        axes.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.0f}%",
            ha="center",
            va="center",
            fontsize=8.5,
            color=colors["surface"],
            fontweight="bold",
        )


def _finish_outcome_axes(axes, colors, keys):
    axes.set_yticks(range(len(keys)))
    axes.set_yticklabels(
        [GROUP_LABELS[tuple(k.split("/"))].replace("\n", " · ") for k in keys]
    )
    axes.set_xlim(0, 100)
    axes.set_xticks([])
    _legend(axes, colors, ncol=2)


def _legend(axes, colors, ncol):
    legend = axes.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=ncol,
        frameon=False,
        fontsize=9,
    )

    for text in legend.get_texts():
        text.set_color(colors["text"])


def _save(figure, name, theme):
    figure.tight_layout()
    figure.savefig(
        FIGURES_DIR / f"{name}-{theme}.png", facecolor=figure.get_facecolor()
    )
    plt.close(figure)


if __name__ == "__main__":
    main()
