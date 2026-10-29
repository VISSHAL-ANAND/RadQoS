import unittest
import numpy as np

from analyze_results import holm_adjust, paired_bootstrap_mean_ci, paired_binary_mcnemar_p, paired_numeric_test, build_threshold_sensitivity

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

class TestThresholdSensitivity(unittest.TestCase):
    def test_expected_grid_and_fallback_accounting(self):
        candidates = []
        rows = [
            ("img1", 4, 100, 0.98, 0.96, 10),
            ("img1", 8, 50, 0.95, 0.92, 20),
            ("img2", 4, 120, 0.97, 0.94, 25),
            ("img2", 8, 60, 0.94, 0.91, 35),
        ]
        for image, ratio, size, global_ssim, regional_ssim, error in rows:
            candidates.append({
                "image": image, "ratio": ratio, "payload_bytes": size,
                "ssim_mean": global_ssim, "lung_region_ssim_p05": regional_ssim,
                "max_abs_error": error,
            })
        lossless = pd.DataFrame([
            {"image": "img1", "payload_bytes": 200},
            {"image": "img2", "payload_bytes": 220},
        ])
        result = build_threshold_sensitivity({
            "candidates": pd.DataFrame(candidates),
            "lossless_quality": lossless,
        })
        self.assertEqual(len(result), 17)
        p1 = result[
            (result["method"] == "P1_lung_region_bound") &
            (result["regional_ssim_p05_threshold"] == 0.95) &
            (result["max_abs_error_threshold"] == 24)
        ].iloc[0]
        self.assertEqual(p1["lossy_feasible_images"], 1)
        self.assertEqual(p1["lossy_infeasible_or_fallback_images"], 1)
        self.assertEqual(p1["n_images"], 2)
        self.assertGreater(p1["mean_payload_bytes"], 0)

if __name__ == "__main__":
    unittest.main()
