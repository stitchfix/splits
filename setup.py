from distutils.core import setup

setup(
    name='splits',
    version='0.0.2',
    author='Thomas Millar, Jeff Magnusson',
    author_email='millar.thomas@gmail.com, magnussj@gmail.com',
    license='MIT',
    description='A library for dealing with splittable files',
    packages = ['splits'],
    long_description='Library for dealing with splittable files',
    url='https://github.com/stitchfix/splits',
    keywords=['split', 'multifile', 'splittable'],
    classifiers=[
        'Intended Audience :: Developers',
    ],
    install_requires=[
        'boto',
        'nose'
    ]
)
