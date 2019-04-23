from distutils.core import setup

from setuptools import find_packages

setup(
    name='drf-messages',
    version=__import__('drf_messages').__version__,
    description='User-to-user messaging system for DRF',
    long_description=open('./README.rst').read(),
    author='Khuram Javed',
    author_email='mail@arnebrodowski.de',
    url='https://github.com/arneb/django-messages',
    packages=find_packages(),
    package_data={
        'drf_messages': [
            'locale/*/LC_MESSAGES/*',
        ]
    },
    classifiers=[
        'Development Status :: 0.0.1',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Framework :: Django',
    ], install_requires=['django', 'djangorestframework']
)
