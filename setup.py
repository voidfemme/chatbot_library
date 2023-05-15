from setuptools import setup, find_packages

setup(
    name="chatbot-library",
    version="0.1.1",
    description="A Python library for creating chatbots using GPT-based models",
    author="voidfemme",
    url="https://github.com/yourusername/chatbot-library",
    packages=find_packages(),
    install_requires=[
        "openai",
        "tiktoken",
        "google-api-python-client",
        "beautifulsoup4",
        "colored",
        "requests",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPL v3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
