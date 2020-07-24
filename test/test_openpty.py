# Test to see if openpty works. (But don't worry if it isn't available.)

import os, unittest
from test.test_support import run_unittest

if not hasattr(os, "openpty"):
    raise unittest.SkipTest, "No openpty() available."


class OpenptyTest(unittest.TestCase):
    def test(self):
        main, subordinate = os.openpty()
        self.addCleanup(os.close, main)
        self.addCleanup(os.close, subordinate)
        if not os.isatty(subordinate):
            self.fail("Subordinate-end of pty is not a terminal.")

        os.write(subordinate, 'Ping!')
        self.assertEqual(os.read(main, 1024), 'Ping!')

def test_main():
    run_unittest(OpenptyTest)

if __name__ == '__main__':
    test_main()
