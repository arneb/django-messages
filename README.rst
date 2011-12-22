==========================================
A user-to-user messaging system for Django
==========================================

Django-messages enables your users to send private messages to each other. 
It provides a basic set of functionality your would expect from such a system.
Every user has an Inbox, an Outbox and a Trash. Messages can be composed and 
there is an easy url-based approach to preloading the compose-form with the 
recipient-user, which makes it extremly easy to put "send xyz a message" links 
on a profile-page.

Currently django-messages comes with these translations:

* de
* fr (thanks froland and dpaccoud)
* es_AR (thanks Juanjo-sfe)
* pl (thanks maczewski)
* es (thanks paz.lupita)
* pt_BR (thanks Diego Martins)
* ru (thanks overkrik)
* nl (thanks krisje8)
* da (thanks Michael Lind Mortensen)
* el (thanks Markos Gogoulos)
* zh_CN (thanks Gene Wu)
* ar (thanks to speedy)
* it (thanks to Sergio Morstabilini)


Versions
--------

* The current trunk/head is compatible with Django 1.2; users of Django 1.1 
  should continue using messages-0.4.x; if you are upgrading from 0.4.x to trunk 
  please read the UPGRADING docs.
* messages-0.4.x is compatible with Django 1.1 (and may work with Django 1.0). 
  The code is avaliable as a Branch.
* messages-0.3 is compatible with Django 1.0, but no longer maintained
* messages-0.2 is still compatible with Django 0.96.x, but not longer maintaned.
  The code is avalibale as a Branch.


Documentation
-------------

The documentation is contained in the /docs/ directory and can be build with 
sphinx. A HTML version of the documentation is available at: 
http://files.arnebrodowski.de/software/django-messages/Documentation/


Install
-------
Download the tar archive, unpack and run python setup.py install or checkout 
the trunk and put the ``django_messages`` folder on your ``PYTHONPATH``. 
Released versions of django-messages are also available on pypi and can be 
installed with easy_install or pip.


Usage
-----

Add ``django_messages`` to your ``INSTALLED_APPS`` setting and add an 
``include('django_messages.urls')`` at any point in your url-conf.

The app includes some default templates, which are pretty simple. They 
extend a template called ``base.html`` and only emit stuff in the block 
``content`` and block ``sidebar``. You may want to use your own templates, 
but the included ones are good enough for testing and getting started.


Dependencies
------------

Django-messages has no external dependencied except for django. But if 
django-notification and/or django-mailer are found it will make use of them. 
Note: as of r65 django-messages will only use django-notification if 
'notification' is also added to the INSTALLES_APPS setting. This has been 
done to make situations possible where notification is on pythonpath but 
should not be used, or where notification is an other python package as 
django-notification which has the same name.



