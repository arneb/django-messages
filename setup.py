from distutils.core import setup

def get_version():
    with open('django_messages/version.txt') as f:
        return f.read().strip()

setup(
    name='django-messages',
    version=get_version(),
    description='User-to-user messaging system for Django',
    long_description=open('README.rst').read(),
    author='Arne Brodowski',
    author_email='mail@arnebrodowski.de',
    url='https://github.com/arneb/django-messages',
    download_url='http://code.google.com/p/django-messages/downloads/list',
    packages=(
        'django_messages',
        'django_messages.templatetags',
        'django_messages.backends',
    ),
    package_data={
        'django_messages': [
            'version.txt',
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