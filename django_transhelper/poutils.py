import io
import polib
import unittest
import tempfile
import os


def merge_po_files(po_file_str1, po_file_str2, output_file_path):
    """Merge two .po files into one"""
    """po_file_str1 and po_file_str2 are strings containing the contents of the .po files"""
    """output_file_path is the path to the output file"""
    """The output file will be overwritten"""
    source_po = polib.pofile(output_file_path)
    metadata = source_po.metadata
    po1 = polib.pofile(po_file_str1)
    po2 = polib.pofile(po_file_str2)

    po1.extend(po2)
    po1.metadata = metadata
    po1.save(output_file_path)


def split_po_file(source_file):
    """Split a .po file into two files: one with translated strings and one with untranslated strings"""
    """Returns a tuple of two strings: (translated, untranslated)"""
    """Can be used to get only the untranslated strings from a .po file"""
    source_po = polib.pofile(source_file)
    missing_translations_po = polib.POFile()

    for entry in source_po:
        if entry.msgid == "":
            continue
        if not entry.translated() or "fuzzy" in entry.flags:
            if "fuzzy" in entry.flags:
                entry.msgstr = ""
                entry.flags.remove("fuzzy")
            missing_translations_po.append(entry)

    source_po = [
        entry
        for entry in source_po
        if entry.msgid != "" and entry.translated() and "fuzzy" not in entry.flags
    ]

    source_po_obj = polib.POFile()
    for entry in source_po:
        assert entry.msgid != ""
        source_po_obj.append(entry)
    source_po_str = source_po_obj.__unicode__()

    missing_translations_str = missing_translations_po.__unicode__()

    # remove first 3 lines from missing_translations_str
    missing_translations_str = "\n".join(missing_translations_str.split("\n")[3:])

    return source_po_str, missing_translations_str


class TestPOFileFunctions(unittest.TestCase):
    def setUp(self):
        self.po_file = """
        # SOME DESCRIPTIVE TITLE.
        # Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
        # This file is distributed under the same license as the PACKAGE package.
        # FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
        #
        #, fuzzy
        msgid ""
        msgstr ""
        "Project-Id-Version: PACKAGE VERSION\\n"
        "Report-Msgid-Bugs-To: \\n"
        "POT-Creation-Date: 2023-08-01 21:31+0000\\n"
        "PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
        "Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
        "Language-Team: LANGUAGE <LL@li.org>\\n"
        "Language: 简体中文\\n"
        "MIME-Version: 1.0\\n"
        "Content-Type: text/plain; charset=UTF-8\\n"
        "Content-Transfer-Encoding: 8bit\\n"

        #: frontend/forms.py:14
        msgid "Phone number"
        msgstr "电话号码"

        #: frontend/forms.py:25
        msgid "I accept the <a href=\\"/tos/\\" target=\\"_new\\" class=\\"text-blue-500 underline\\">terms and conditions</a>"
        msgstr ""

        #: frontend/forms.py:28
        msgid "You must accept the terms and conditions."
        msgstr "您必须接受这些条款和条件."
        """

    def test_move_missing_translations(self):
        source_file = tempfile.NamedTemporaryFile(delete=False)
        source_file.write(self.po_file.encode())
        source_file.close()

        source_po_str, missing_translations_str = split_po_file(source_file.name)
        self.assertIn('msgid ""\nmsgstr ""', source_po_str)
        self.assertIn('msgid "Phone number"\nmsgstr "电话号码"', source_po_str)
        self.assertIn(
            'msgid "You must accept the terms and conditions."\nmsgstr "您必须接受这些条款和条件."',
            source_po_str,
        )
        self.assertIn(
            'msgid ""\n"I accept the <a href=\\"/tos/\\" target=\\"_new\\" class=\\"text-blue-500 "\n"underline\\">terms and conditions</a>"\nmsgstr ""',
            missing_translations_str,
        )

        os.unlink(source_file.name)

    def test_move_fuzzy_translations(self):
        fuzzy_po_file = """
        # SOME DESCRIPTIVE TITLE.
        # Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
        # This file is distributed under the same license as the PACKAGE package.
        # FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
        #
        #, fuzzy
        msgid ""
        msgstr ""
        "Project-Id-Version: PACKAGE VERSION\\n"
        "Report-Msgid-Bugs-To: \\n"
        "POT-Creation-Date: 2023-08-01 21:31+0000\\n"
        "PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
        "Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
        "Language-Team: LANGUAGE <LL@li.org>\\n"
        "Language: 简体中文\\n"
        "MIME-Version: 1.0\\n"
        "Content-Type: text/plain; charset=UTF-8\\n"
        "Content-Transfer-Encoding: 8bit\\n"

        #: frontend/forms.py:14
        #, fuzzy
        msgid "Phone number"
        msgstr "电话号码"
        """

        source_file = tempfile.NamedTemporaryFile(delete=False)
        source_file.write(fuzzy_po_file.encode())
        source_file.close()

        source_po_str, missing_translations_str = split_po_file(source_file.name)
        self.assertNotIn('msgid "Phone number"\nmsgstr "电话号码"', source_po_str)
        self.assertIn('msgid "Phone number"\nmsgstr ""', missing_translations_str)

        os.unlink(source_file.name)

    def test_merge_po_files(self):
        po_file_str1 = 'msgid "Hello"\nmsgstr "你好"'
        po_file_str2 = 'msgid "Goodbye"\nmsgstr "再见"'
        output_file_path = tempfile.NamedTemporaryFile(delete=False).name
        merge_po_files(po_file_str1, po_file_str2, output_file_path)
        with open(output_file_path, "r") as f:
            merged_po_file_str = f.read()
        self.assertIn('msgid "Hello"\nmsgstr "你好"', merged_po_file_str)
        self.assertIn('msgid "Goodbye"\nmsgstr "再见"', merged_po_file_str)

        os.unlink(output_file_path)


if __name__ == "__main__":
    unittest.main()
