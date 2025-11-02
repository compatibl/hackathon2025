import setuptools

with open('./README.md', 'r') as readme_file:
    readme = readme_file.read()

# Internal requirements (exclude when building from monorepo)
install_requires = [
    "runtime>=2.0.5",
    "convince>=0.0.3"
]

# Third-party requirements
with open('./tools/cl/hackathon/package_requirements.txt') as hackathon_package_requirements:
    install_requires.extend(line.strip() for line in hackathon_package_requirements.readlines())

setuptools.setup(
    name='hackathon',
    version='0.0.1',
    author='The Project Contributors',
    description='2025 QuantMinds-CompatibL Hackathon',
    license='Apache Software License',
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=install_requires,
    url='https://github.com/compatibl/hackathon2025',
    project_urls={
        'Source Code': 'https://github.com/compatibl/hackathon2025',
    },
    packages=setuptools.find_namespace_packages(
        where='.',
        include=['cl.hackathon', 'cl.hackathon.*'],
        exclude=['tests', 'tests.*']
    ),
    package_dir={'': '.'},
    classifiers=[
        # Alpha - will attempt to avoid breaking changes but they remain possible
        'Development Status :: 3 - Alpha',

        # Audience and topic
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',

        # License
        'License :: OSI Approved :: Apache Software License',

        # Runs on Python 3.11 and later releases
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',

        # Operating system
        'Operating System :: OS Independent',
    ],
)
