#!/usr/bin/env python
# encoding: utf-8

import unittest

from piSync import print_something

class TestModuleDemo(unittest.TestCase):
    def test_print_something(self):
        status = print_something("My value")
        print(status, flush=True)
        self.assertEqual(status, "My value")