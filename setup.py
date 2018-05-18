from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='splits',
    version='0.1.9',
    author='Thomas Millar, Jeff Magnusson',
    author_email='millar.thomas@gmail.com, magnussj@gmail.com',
    license='MIT',
    description='A library for dealing with splittable files',
    packages=['splits'],
    long_description=readme,
    url='https://github.com/stitchfix/splits',
    keywords=['split', 'multifile', 'splittable'],
    classifiers=[
        'Intended Audience :: Developers',
    ],
    install_requires=['boto', 'nose'],
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
)
