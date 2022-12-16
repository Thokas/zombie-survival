import os
import sys
import unittest

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner()

    test_runner.verbosity = 2  # print info about every test
    root_dir = os.path.dirname(__file__)
    test_loader = unittest.TestLoader()
    tests = test_loader.discover(start_dir=root_dir)
    result = test_runner.run(tests)
    successful = result.wasSuccessful()
    sys.exit(not successful)
