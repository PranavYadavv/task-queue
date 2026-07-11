"""Tests for task-queue core module."""

import unittest
from src.core import TaskQueue


class TestTaskQueue(unittest.TestCase):
    def setUp(self):
        self.instance = TaskQueue()

    def test_initialize(self):
        self.instance.initialize()
        self.assertTrue(self.instance._initialized)

    def test_process_without_init_raises(self):
        with self.assertRaises(RuntimeError):
            self.instance.process([{"id": 1}])

    def test_process_returns_results(self):
        self.instance.initialize()
        results = self.instance.process([{"id": 1}, {"id": 2}])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["status"], "processed")

    def test_shutdown(self):
        self.instance.initialize()
        self.instance.shutdown()
        self.assertFalse(self.instance._initialized)


if __name__ == "__main__":
    unittest.main()
