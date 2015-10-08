from distutils.core import setup

setup(
    name='rublon',
    version='1.0',
    packages=['rublon'],
    author='Sebastian Buczynski',
    author_email='poczta@enforcer.pl',
    include_package_data=True,
    install_requires=[
        'six==1.9.0',
        'tox==2.1.1',
        'nose==1.3.4'
    ]
)
