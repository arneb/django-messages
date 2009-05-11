from distutils.core import setup

setup(
    name='django-messages',
    version=__import__('messages').__version__,
    description='User-to-user messaging system for Django',
    author='Arne Brodowski',
    author_email='mail@arnebrodowski.de',
    url='http://code.google.com/p/django-messages/',
    packages=(
        'messages',
        'messages.templatetags',
    ),
    package_data={
        'messages': [
            'templates/messages/*',
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