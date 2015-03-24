from distutils.core import setup

setup(
    name='django-messages',
    version=__import__('django_messages').__version__,
    description='User-to-user messaging system for Django',
    long_description=open('README.rst').read(),
    author='Arne Brodowski',
    author_email='mail@arnebrodowski.de',
    url='https://github.com/arneb/django-messages',
    install_requires=[
        'Django'
    ],
    packages=(
        'django_messages',
        'django_messages.templatetags',
    ),
    package_data={
        'django_messages': [
            'templates/django_messages/*',
            'templates/notification/*/*',
            'locale/*/LC_MESSAGES/*',
        ]
    },
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Framework :: Django',
    ),
)
