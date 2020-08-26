import f5_lbaasv2_bigiq_dirver

from setuptools import find_packages
from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='f5-openstack-lbaasv2-bigiq-driver',
      description='F5 Networks BIG-IQ Driver for OpenStack LBaaSv2',
      version=f5_lbaasv2_bigiq_dirver.__version__,
      long_description=readme(),
      long_description_content_type='text/x-rst',
      author='Qin Zhao',
      author_email='q.zhao@f5.com',
      url='https://github.com/F5Networks/f5-openstack-lbaasv2-bigiq-driver',
      # Runtime dependencies.
      install_requires=[],
      packages=find_packages(exclude=('test', 'neutron_lbaas')),
      classifiers=['Development Status :: 5 - Production/Stable',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Intended Audience :: System Administrators']
      )
