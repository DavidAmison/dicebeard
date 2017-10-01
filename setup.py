from distutils.core import setup

setup(
    name='DiceBeard',
    version='0.1dev',
    packages=['dicebeard',
              'dicebeard.skb_roll'],
    package_dir={'': 'python'},
    license='CC-0',
    long_description=open('README.md').read(),
)
