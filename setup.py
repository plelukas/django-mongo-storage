import os
from setuptools import setup
from pip.req import parse_requirements
from setuptools import setup, find_packages


__description__ = 'Mongo Storage Module'
__license__ = 'LGPL'
__author__ = 'Lukasz Plewnia'
__email__ = 'plelukas@gmail.com'


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_require_gen = parse_requirements('requirements.txt', session=False)
# reqs is a list of requirement
# e.g. ['django==1.8.1', ]
install_requires = [str(ir.req) for ir in install_require_gen]

# parse_requirements() returns generator of pip.req.InstallRequirement objects
tests_require_gen = parse_requirements('requirements_tests.txt', session=False)
# reqs is a list of requirement
# e.g. ['django==1.8.1', ]
tests_requires = [str(ir.req) for ir in tests_require_gen]


setup(
    name='django-mongo-storage',
    version=__import__('django-mongo-storage').__version__,
    packages=find_packages(),
    include_package_data=True,
    license=__license__,
    description=__description__,
    long_description=README,
    url='',
    author=__author__,
    author_email=__email__,
    tests_require=tests_requires,
    install_requires=install_requires,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: LGPL Liceance',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
