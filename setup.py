from setuptools import setup

setup(
    name='moneyworks',
    version='1.1.0',
    description='A python API for Cognito Moneyworks accounting software',
    long_description='A python API for Cognito Moneyworks accounting software',
    url='http://github.com/ari/moneyworks-cli/',

    author='Aristedes Maniatis',
    author_email='ari@ish.com.au',

    license="APL2",

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='api moneyworks accounting',

    data_files = [("", ["LICENSE"])],
    packages=["moneyworks"],
    install_requires=['requests']
)