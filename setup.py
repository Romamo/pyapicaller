from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='pyapicaller',  # Ensure this matches the package name
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'jsonref==1.1.0',
        'pydantic==2.9.2',
        'openai==1.52.0',
        'pyyaml==6.0.2'
    ],
    author='Roman Medvedev',
    author_email='your.email@example.com',  # Replace with your actual email
    description='A simple API caller package for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Romamo/pyapicaller',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.10',
)
