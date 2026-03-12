"""
Test suite for Text Utilities Library (Locking Experiment).

All 9 functions must be present in text_utils.py:
  capitalize_words, count_words, truncate,
  is_palindrome, reverse_words, count_vowels,
  slugify, strip_punctuation, word_frequency
"""
import pytest

# ── capitalize_words ──────────────────────────────────────────────────────────

def test_capitalize_words_basic():
    from text_utils import capitalize_words
    assert capitalize_words("hello world") == "Hello World"

def test_capitalize_words_single():
    from text_utils import capitalize_words
    assert capitalize_words("python") == "Python"

def test_capitalize_words_already_capitalized():
    from text_utils import capitalize_words
    assert capitalize_words("Hello World") == "Hello World"

def test_capitalize_words_empty():
    from text_utils import capitalize_words
    assert capitalize_words("") == ""

def test_capitalize_words_mixed_case():
    from text_utils import capitalize_words
    assert capitalize_words("hELLO wORLD") == "HELLO WORLD"  # title() behavior: only first letter up

# ── count_words ───────────────────────────────────────────────────────────────

def test_count_words_basic():
    from text_utils import count_words
    assert count_words("hello world") == 2

def test_count_words_single():
    from text_utils import count_words
    assert count_words("hello") == 1

def test_count_words_empty():
    from text_utils import count_words
    assert count_words("") == 0

def test_count_words_whitespace_only():
    from text_utils import count_words
    assert count_words("   ") == 0

def test_count_words_many():
    from text_utils import count_words
    assert count_words("one two three four five") == 5

# ── truncate ──────────────────────────────────────────────────────────────────

def test_truncate_no_op():
    from text_utils import truncate
    assert truncate("hi", 10) == "hi"

def test_truncate_exact():
    from text_utils import truncate
    assert truncate("hello", 5) == "hello"

def test_truncate_basic():
    from text_utils import truncate
    assert truncate("hello world", 8) == "hello..."

def test_truncate_custom_ellipsis():
    from text_utils import truncate
    assert truncate("hello world", 7, "..") == "hello.."

def test_truncate_short_max_len():
    from text_utils import truncate
    # max_len <= len(ellipsis): return ellipsis[:max_len]
    assert truncate("hello", 2) == ".."

# ── is_palindrome ─────────────────────────────────────────────────────────────

def test_is_palindrome_true():
    from text_utils import is_palindrome
    assert is_palindrome("racecar") is True

def test_is_palindrome_case_insensitive():
    from text_utils import is_palindrome
    assert is_palindrome("Racecar") is True

def test_is_palindrome_false():
    from text_utils import is_palindrome
    assert is_palindrome("hello") is False

def test_is_palindrome_single_char():
    from text_utils import is_palindrome
    assert is_palindrome("a") is True

def test_is_palindrome_with_spaces():
    from text_utils import is_palindrome
    # strip only — spaces inside are kept after strip
    assert is_palindrome("  racecar  ") is True

# ── reverse_words ─────────────────────────────────────────────────────────────

def test_reverse_words_basic():
    from text_utils import reverse_words
    assert reverse_words("hello world foo") == "foo world hello"

def test_reverse_words_single():
    from text_utils import reverse_words
    assert reverse_words("hello") == "hello"

def test_reverse_words_two():
    from text_utils import reverse_words
    assert reverse_words("a b") == "b a"

def test_reverse_words_empty():
    from text_utils import reverse_words
    assert reverse_words("") == ""

# ── count_vowels ──────────────────────────────────────────────────────────────

def test_count_vowels_basic():
    from text_utils import count_vowels
    assert count_vowels("hello") == 2

def test_count_vowels_case_insensitive():
    from text_utils import count_vowels
    assert count_vowels("AEIOU") == 5

def test_count_vowels_none():
    from text_utils import count_vowels
    assert count_vowels("rhythm") == 0

def test_count_vowels_sentence():
    from text_utils import count_vowels
    assert count_vowels("Hello World") == 3

def test_count_vowels_empty():
    from text_utils import count_vowels
    assert count_vowels("") == 0

# ── slugify ───────────────────────────────────────────────────────────────────

def test_slugify_basic():
    from text_utils import slugify
    assert slugify("Hello World") == "hello-world"

def test_slugify_punctuation():
    from text_utils import slugify
    assert slugify("Hello, World!") == "hello-world"

def test_slugify_multiple_spaces():
    from text_utils import slugify
    assert slugify("Hello   World") == "hello-world"

def test_slugify_already_slug():
    from text_utils import slugify
    assert slugify("hello-world") == "hello-world"

def test_slugify_leading_trailing():
    from text_utils import slugify
    assert slugify("  Hello World  ") == "hello-world"

# ── strip_punctuation ─────────────────────────────────────────────────────────

def test_strip_punctuation_basic():
    from text_utils import strip_punctuation
    assert strip_punctuation("Hello, World!") == "Hello World"

def test_strip_punctuation_no_punctuation():
    from text_utils import strip_punctuation
    assert strip_punctuation("Hello World") == "Hello World"

def test_strip_punctuation_only_punctuation():
    from text_utils import strip_punctuation
    assert strip_punctuation("...!!!") == ""

def test_strip_punctuation_empty():
    from text_utils import strip_punctuation
    assert strip_punctuation("") == ""

def test_strip_punctuation_mixed():
    from text_utils import strip_punctuation
    result = strip_punctuation("It's a test.")
    assert "'" not in result and "." not in result

# ── word_frequency ────────────────────────────────────────────────────────────

def test_word_frequency_basic():
    from text_utils import word_frequency
    result = word_frequency("the cat sat on the mat")
    assert result == {"the": 2, "cat": 1, "sat": 1, "on": 1, "mat": 1}

def test_word_frequency_case_insensitive():
    from text_utils import word_frequency
    result = word_frequency("Hello hello HELLO")
    assert result == {"hello": 3}

def test_word_frequency_single():
    from text_utils import word_frequency
    assert word_frequency("hello") == {"hello": 1}

def test_word_frequency_empty():
    from text_utils import word_frequency
    assert word_frequency("") == {}

def test_word_frequency_with_punctuation():
    from text_utils import word_frequency
    result = word_frequency("cat, cat. cat!")
    assert result.get("cat", 0) == 3
