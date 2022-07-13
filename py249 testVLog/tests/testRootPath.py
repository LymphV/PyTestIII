import unittest

from vUtil.vLog import rootPath


class TestRootPath(unittest.TestCase):
    def testRootPath (this):
        if __name__ == '__main__':
            path = 'C:\\Users\\ict\\LymphV\\程序\\试验品\\Py试验品III\\py249 testVLog\\tests'
        else:
            path = 'C:\\Users\\ict\\LymphV\\程序\\试验品\\Py试验品III\\py249 testVLog'
        this.assertEqual(rootPath, path)


if __name__ == '__main__':
    TestRootPath().testRootPath()