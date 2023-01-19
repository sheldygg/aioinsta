import setuptools


def get_description():
    with open('README.rst', 'r', encoding='utf-8') as f:
        return f.read()


setuptools.setup(
    name="aioinsta",
    version="1",
    license='MIT',
    author="sheldy",
    description="Tool for parse instagram data",
    url="https://github.com/sheldygg/aioinsta",
    packages=setuptools.find_packages(),
    long_description=get_description(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ],
    install_requires=[
        'aiohttp'
    ],
)