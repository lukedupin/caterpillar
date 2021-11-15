from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='caterpillar-api',
    version='v1.43',
    packages=['caterpillar-api'],
    url='https://github.com/lukedupin/caterpillar',
    # I explain this later on
    license='MIT',
    author='Luke Dupin',
    author_email='lukedupin@gmail.com',
    description='🐛 Caterpillar Api, field management for Django without the boiler-plate.',
    keywords = ['DJANGO', 'API', 'REST', 'JSON', 'JSONP', 'JSON-P'],
    install_requires=['Django'],
    classifiers=[
        'Development Status :: 4 - Beta',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',
        # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)