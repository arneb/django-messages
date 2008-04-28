from distutils.core import setup

setup(name='messages',
      version='0.1',
      description='User-to-user messaging system for Django',
      author='Arne Brodowski',
      author_email='mail@arnebrodowski.de',
      url='http://code.google.com/p/django-messages/',
      packages=['messages', 'messages.templatetags'],
      package_dir={'messages': 'messages'},
      package_data={'messages': ['templates/messages/*.html']},
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      )