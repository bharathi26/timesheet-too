""" A simple, but useful library for all your timesheet-based needs.
"""
from setuptools import setup

doclines = __doc__.split('\n')

setup(
        name = "timesheet",
        version = "0.0.1",
        author = "Wayne Werner",
        author_email = "wayne@waynewerner.com",
        description = doclines,
        keywords = "timesheet time productivity schedule",
        packages=['timesheet', 'tests'],
        test_suite="tests",
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Utilities",
        ],
)
