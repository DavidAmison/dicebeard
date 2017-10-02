from distutils.core import setup

setup(
    name='DiceBeard',
    version='0.1dev',
    packages=['dicebeard',
              'dicebeard.skb_roll'],
    package_dir={'': 'python'},
    license='CC-0',
    install_requires=[x.strip() for x in open("requirements.txt").readlines()],
    long_description=open('README.md').read(),
    dependency_links=['https://github.com/nasfarley88/pydice.git/tarball/master#egg']
)
