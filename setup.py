from distutils.core import setup

setup(
    name='splits',
    version='0.0.1',
    author='Thomas Millar, Jeff Magnusson',
    author_email='millar.thomas@gmail.com, magnussj@gmail.com',
    license='MIT',
    description='A Python library for dealing with splittable files',
    long_description='Stitchfix Library for dealing with splittable files',
    url='https://github.com/stitchfix/splits',
    keywords=['split', 'multifile', 'splittable'],
    classifiers=[
        'Programming Language :: Python :: 2.7.2',
    ],
    install_requires = [
        'boto',
        'nose'
    ]
)
