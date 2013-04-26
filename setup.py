from setuptools import setup, find_packages
import os

version = open(os.path.join("akorn_admin", "version.txt")).read().strip()

setup(name='akorn_admin',
      version=version,
      description="",
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Akorn',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['akorn_admin'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
)
