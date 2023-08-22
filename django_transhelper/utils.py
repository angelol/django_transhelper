import unittest
import re


def extract_code_blocks(input_string: str, keyword: str = None) -> str:
    """Extracts code blocks from a string and returns them as a single string."""
    """If keyword is provided, only code blocks after the keyword will be extracted."""
    """Can be used to extract the code from LLM outputs."""
    if keyword:
        keyword_index = input_string.find(keyword)
        if keyword_index != -1:
            input_string = input_string[keyword_index:]

    pattern = r"```.*?\n(.*?)```"
    matches = re.findall(pattern, input_string, re.DOTALL)

    code_string = "\n".join(match.strip() for match in matches)
    return code_string


class TestExtractCodeBlocks(unittest.TestCase):
    def test_no_code_blocks(self):
        self.assertEqual(extract_code_blocks("No code blocks here."), "")

    def test_single_code_block(self):
        self.assertEqual(
            extract_code_blocks(
                "Here is a code block:\n```\nprint('Hello, world!')\n```"
            ),
            "print('Hello, world!')",
        )

    def test_multiple_code_blocks(self):
        self.assertEqual(
            extract_code_blocks(
                "Here are two code blocks:\n```\nprint('Hello, world!')\n```\n```\nprint('Goodbye, world!')\n```"
            ),
            "print('Hello, world!')\nprint('Goodbye, world!')",
        )

    def test_code_block_with_language_specifier(self):
        self.assertEqual(
            extract_code_blocks(
                "Here is a Python code block:\n```python\nprint('Hello, world!')\n```"
            ),
            "print('Hello, world!')",
        )

    def test_code_block_with_keyword(self):
        self.assertEqual(
            extract_code_blocks("Answer:\n```\nprint('Hello, world!')\n```", "Answer"),
            "print('Hello, world!')",
        )

    def test_no_code_block_with_keyword(self):
        self.assertEqual(extract_code_blocks("No code block here.", "Answer"), "")


if __name__ == "__main__":
    unittest.main()
