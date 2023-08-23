from django.conf import settings
from django.core.management import BaseCommand, call_command
from babel.core import Locale
import openai
import os
from django_transhelper.utils import extract_code_blocks
from django_transhelper.poutils import split_po_file, merge_po_files
from langchain.text_splitter import RecursiveCharacterTextSplitter

encoding_name = "cl100k_base"  # GPT-4 uses the cl100k_base encoding
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name=encoding_name, chunk_size=1500, chunk_overlap=0
)
openai.api_key = settings.OPENAI_API_KEY


class Command(BaseCommand):
    help = "This command generates or updates .po files for all languages defined in settings.LANGUAGES. Translations will be automatically generated using OpenAI's GPT-4."

    def handle(self, *args, **options):
        # filter out default language
        languages = [
            (code, language_name)
            for code, language_name in settings.LANGUAGES
            if code != settings.LANGUAGE_CODE
        ]
        # Convert all language codes to gettext format
        locales = [convert_locale(code) for code, _ in languages]
        # Call makemessages command with the list of locales
        call_command(
            "makemessages",
            locale=locales,
            ignore=["venv"],
            no_obsolete=True,
            verbosity=0,
            extensions=["py", "html", "inc", "txt"],
        )

        # Read, modify and write back the .po files
        for locale, (code, language_name) in zip(locales, languages):
            print(f"Translating to {language_name}...")
            po_file_path = os.path.join(
                settings.BASE_DIR, "locale", locale, "LC_MESSAGES", "django.po"
            )

            translated, untranslated = split_po_file(po_file_path)
            if not untranslated:
                print(
                    f"Skipping {language_name} because there are no untranslated strings."
                )
                continue

            texts = text_splitter.split_text(untranslated)
            chunks = []
            for text in texts:
                # print(f"Translating chunk:\n{text}")
                chunk = translate_content(text, language_name)
                chunks.append(chunk)

            modified_content = "\n\n".join(chunks)

            merge_po_files(translated, modified_content, po_file_path)

        call_command("compilemessages", verbosity=0)


def translate_content(content, language_name):
    result = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": f"Translate to {language_name}:\n\n{content}"},
        ],
        temperature=0.0,
        timeout=1200,
    )
    translated = extract_code_blocks(result.choices[0].message["content"])
    return translated


SYSTEM_MESSAGE = """You are a professional translator that is proficient in all languages and will provide accurate translations of .po files. Please answer with the entire .po file (including preamble comments). The output must be a valid .po file. Remember that when the msgid string ends in a newline, the msgstr must also end in a newline. And if the msgid string does not end in a newline, then the msgstr should likewise not have a newline at the end. Always put your response in a code block."""


def convert_locale(language_code):
    """Convert a language code from Django format to gettext format."""
    locale = Locale.parse(language_code, sep="-")
    return str(locale)
