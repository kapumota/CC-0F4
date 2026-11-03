"""Pruebas del selector SQuAD sobre una estructura minima: NO datos experimentales."""
import unittest
from .prepare_real_data import select_subset, git_blob_sha1

class SQuADSelectionTests(unittest.TestCase):
    def test_git_blob_known(self):
        self.assertEqual(git_blob_sha1(b"test"), "30d74d258442c7c65512eafab474568dd706c430")

    def test_invalid_source_fails(self):
        with self.assertRaises(ValueError):
            select_subset({"data": []})

if __name__ == "__main__":
    unittest.main()
