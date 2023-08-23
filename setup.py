from setuptools import setup, find_packages

setup(
    name="django_transhelper",
    description="""Adds the management command `trans` to generate or update .po files for all languages defined in settings.LANGUAGES. Translations will be automatically generated using OpenAI's GPT-4.""",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django",
        "langchain",
        "tiktoken",
        "polib",
        "babel",
        "openai",
        "openai-multi-client",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
