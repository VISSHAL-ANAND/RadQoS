import unittest
import numpy as np

from analyze_results import holm_adjust, paired_bootstrap_mean_ci, paired_binary_mcnemar_p, paired_numeric_test

class TestHolmAdjustment(unittest.TestCase):
    def test_known_values(self):
        got = holm_adjust([0.01, 0.04, 0.03])
        np.testing.assert_allclose(got, [0.03, 0.06, 0.06])

    def test_empty_and_single(self):
        self.assertEqual(holm_adjust([]), [])
        self.assertEqual(holm_adjust([0.2]), [0.2])

    def test_invalid_p_value_rejected(self):
        with self.assertRaises(ValueError):
            holm_adjust([1.2])

class TestPairedStatistics(unittest.TestCase):
    def test_bootstrap_is_deterministic(self):
        a = paired_bootstrap_mean_ci([1, 2, 3, 4], seed=42, n_resamples=100)
        b = paired_bootstrap_mean_ci([1, 2, 3, 4], seed=42, n_resamples=100)
        self.assertEqual(a, b)

    def test_wilcoxon_all_zero_is_one(self):
        self.assertEqual(paired_numeric_test([0, 0, 0]), 1.0)

    def test_mcnemar_no_discordance(self):
        p, b, c = paired_binary_mcnemar_p([0, 1, 1], [0, 1, 1])
        self.assertEqual(p, 1.0)
        self.assertEqual((b, c), (0, 0))

    def test_mcnemar_balanced_discordance(self):
        p, b, c = paired_binary_mcnemar_p([0, 1], [1, 0])
        self.assertEqual(p, 1.0)
        self.assertEqual((b, c), (1, 1))

    def test_mcnemar_invalid_values_rejected(self):
        with self.assertRaises(ValueError):
            paired_binary_mcnemar_p([0, 2], [1, 0])

if __name__ == "__main__":
    unittest.main()
