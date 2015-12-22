
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


setup(
    name='dynaconf',
    version="0.2.5",
    url='https://github.com/rochacbruno/dynaconf',
    license='MIT',
    author="Bruno Rocha",
    author_email="rochacbruno@gmail.com",
    description='Load Dynamic config',
    long_description="Load your configs in Dynamic way",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any'
)
