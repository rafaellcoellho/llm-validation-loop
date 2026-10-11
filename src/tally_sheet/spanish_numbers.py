import unicodedata

DIGIT_WORDS = {
    "cero": 0,
    "uno": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
}


def parse_digit_words(text):
    words = [_normalize(word) for word in text.split(",") if word.strip()]
    if not words:
        raise ValueError(f"no digit words in {text!r}")

    digits = [_digit_of(word, text) for word in words]

    return int("".join(str(digit) for digit in digits))


def _normalize(word):
    decomposed = unicodedata.normalize("NFKD", word.strip().lower())

    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _digit_of(word, text):
    if word not in DIGIT_WORDS:
        raise ValueError(f"unknown digit word {word!r} in {text!r}")

    return DIGIT_WORDS[word]
