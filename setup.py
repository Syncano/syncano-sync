from setuptools import find_packages, setup

setup(
    name='syncano-sync',
    version='0.1',
    description='Syncano synchronization utility',
    author='Marcin Swiderski',
    author_email='marcin.swiderski@syncano.com',
    url='https://syncano.com/',
    packages=find_packages(),
    install_requires=['syncano>=5.0', 'PyYaml>=3.11'],
    entry_points="""
        [console_scripts]
        syncano-sync=syncano_sync.main:main
    """
)
