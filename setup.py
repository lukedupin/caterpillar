from setuptools import setup

setup(
    name='caterpillar-api',
    version='1.43',
    packages=['caterpillar-api'],
    url='https://github.com/lukedupin/caterpillar',
    license='MIT',
    author='Luke Dupin',
    author_email='lukedupin@gmail.com',
    description='🐛 Caterpillar Api, field management for Django without the boiler-plate.',
    keywords = ['DJANGO', 'API', 'REST', 'JSON', 'JSONP', 'JSON-P'],
)


setup(
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  install_requires=[            # I get to this in a second
          'validators',
          'beautifulsoup4',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)