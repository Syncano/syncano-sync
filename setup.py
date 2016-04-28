from setuptools import find_packages, setup

setup(
    name='syncano-sync',
    version='1.0',
    description='Python Distribution Utilities',
    author='Marcin Swiderski',
    author_email='marcin.swiderski@syncano.com',
    url='https://syncano.com/',
    packages=find_packages(),
    install_requires=['syncano'],
    entry_points="""
        [console_scripts]
        syncano-sync=syncano_sync.main:main
    """
)
