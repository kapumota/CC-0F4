"""Pruebas de contratos: NO constituyen resultados experimentales de SQuAD."""
import unittest

from .prepare_real_data import (EXPECTED_ARTICLES, EXPECTED_PASSAGES,
                                EXPECTED_QUESTIONS, choose_calibration_titles,
                                extract_dataset, git_blob_sha1)


class PreparationContractTests(unittest.TestCase):
    def test_sha1_git_blob(self):
        self.assertEqual(git_blob_sha1(b"test"), "30d74d258442c7c65512eafab474568dd706c430")

    def test_partition_disjoint_and_deterministic(self):
        titles = [f"Articulo verificador {i}" for i in range(EXPECTED_ARTICLES)]
        a = choose_calibration_titles(titles)
        b = choose_calibration_titles(list(reversed(titles)))
        self.assertEqual(a, b)
        self.assertEqual(len(a), 12)
        self.assertEqual(len(a & (set(titles) - a)), 0)

    def test_incomplete_data_rejected(self):
        with self.assertRaises(ValueError):
            extract_dataset({"data": []})

    def test_fixed_expected_sizes(self):
        self.assertEqual((EXPECTED_ARTICLES, EXPECTED_PASSAGES, EXPECTED_QUESTIONS),
                         (48, 2067, 10570))


if __name__ == "__main__":
    unittest.main()
