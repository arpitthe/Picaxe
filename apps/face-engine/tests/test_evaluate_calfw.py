"""
Unit tests for the CALFW evaluation script logic.
"""

import unittest
from pathlib import Path
import tempfile
import os

from scripts.evaluate_calfw import load_pairs, compute_metrics, limit_pairs, validate_args
from argparse import Namespace

class TestEvaluateCALFW(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pairs_file = Path(self.temp_dir.name) / "pairs_CALFW.txt"
        
    def tearDown(self):
        self.temp_dir.cleanup()
        
    def test_load_pairs_valid(self):
        content = (
            "person1_01.jpg 1\n"
            "person1_02.jpg 1\n"
            "person2_01.jpg 0\n"
            "person3_01.jpg 0\n"
            "person4_01.jpg 10\n"
            "person4_02.jpg 10\n"
        )
        self.pairs_file.write_text(content)
        
        pairs = load_pairs(self.pairs_file)
        self.assertEqual(len(pairs), 3)
        self.assertEqual(pairs[0], ("person1_01.jpg", "person1_02.jpg", 1))
        self.assertEqual(pairs[1], ("person2_01.jpg", "person3_01.jpg", 0))
        # Label 10 should be normalized to 1
        self.assertEqual(pairs[2], ("person4_01.jpg", "person4_02.jpg", 1))

    def test_load_pairs_odd_lines(self):
        content = (
            "person1_01.jpg 1\n"
            "person1_02.jpg 1\n"
            "person2_01.jpg 0\n"
        )
        self.pairs_file.write_text(content)
        
        with self.assertRaises(ValueError):
            load_pairs(self.pairs_file)

    def test_load_pairs_inconsistent_labels(self):
        content = (
            "person1_01.jpg 1\n"
            "person1_02.jpg 0\n"
        )
        self.pairs_file.write_text(content)
        
        with self.assertRaises(ValueError):
            load_pairs(self.pairs_file)

    def test_compute_metrics(self):
        # sims: 0.9, 0.8, 0.4, 0.2
        # labels: 1, 1, 0, 0
        similarities = [0.9, 0.8, 0.4, 0.2]
        labels = [1, 1, 0, 0]
        thresholds = [0.5, 0.85]
        
        results = compute_metrics(similarities, labels, thresholds)
        
        # For th=0.5: Preds: [1, 1, 0, 0]. tp=2, tn=2, fp=0, fn=0, acc=1.0
        res_05 = next(r for r in results if r["threshold"] == 0.5)
        self.assertEqual(res_05["tp"], 2)
        self.assertEqual(res_05["fp"], 0)
        self.assertEqual(res_05["tn"], 2)
        self.assertEqual(res_05["fn"], 0)
        self.assertEqual(res_05["accuracy"], 1.0)
        
        # For th=0.85: Preds: [1, 0, 0, 0]. tp=1, tn=2, fp=0, fn=1, acc=0.75
        res_085 = next(r for r in results if r["threshold"] == 0.85)
        self.assertEqual(res_085["tp"], 1)
        self.assertEqual(res_085["fp"], 0)
        self.assertEqual(res_085["fn"], 1)
        self.assertEqual(res_085["accuracy"], 0.75)
        self.assertEqual(res_085["recall"], 0.5)

    def test_validate_args_max_pairs_zero(self):
        args = Namespace(dataset_root="dummy", max_pairs=0)
        with self.assertRaises(ValueError):
            validate_args(args)
            
    def test_validate_args_max_pairs_negative(self):
        args = Namespace(dataset_root="dummy", max_pairs=-5)
        with self.assertRaises(ValueError):
            validate_args(args)

    def test_limit_pairs_correctly(self):
        # 3 positive pairs, 3 negative pairs
        pairs = [
            ("p1", "p2", 1), ("p3", "p4", 1), ("p5", "p6", 1),
            ("n1", "n2", 0), ("n3", "n4", 0), ("n5", "n6", 0)
        ]
        
        # Limit to 2 (should be 1 pos, 1 neg)
        limited = limit_pairs(pairs, 2)
        self.assertEqual(len(limited), 2)
        self.assertEqual(sum(1 for p in limited if p[2] == 1), 1)
        self.assertEqual(sum(1 for p in limited if p[2] == 0), 1)
        
        # Limit to 3 (should be 2 pos, 1 neg deterministically)
        limited_odd = limit_pairs(pairs, 3)
        self.assertEqual(len(limited_odd), 3)
        self.assertEqual(sum(1 for p in limited_odd if p[2] == 1), 2)
        self.assertEqual(sum(1 for p in limited_odd if p[2] == 0), 1)
        
        # Limit to larger than dataset (safe handling)
        limited_large = limit_pairs(pairs, 10)
        self.assertEqual(len(limited_large), 6)
        self.assertEqual(limited_large, pairs[:3] + pairs[3:])
        
        # No limit
        limited_none = limit_pairs(pairs, None)
        self.assertEqual(len(limited_none), 6)
        self.assertEqual(limited_none, pairs)
        
    def test_limit_pairs_unbalanced_available(self):
        # 1 positive pair, 4 negative pairs
        pairs = [
            ("p1", "p2", 1),
            ("n1", "n2", 0), ("n3", "n4", 0), ("n5", "n6", 0), ("n7", "n8", 0)
        ]
        
        # Limit to 4
        # Target is 2 pos, 2 neg, but only 1 pos available. 
        # Should take 1 pos, and 3 neg to fill the limit of 4.
        limited = limit_pairs(pairs, 4)
        self.assertEqual(len(limited), 4)
        self.assertEqual(sum(1 for p in limited if p[2] == 1), 1)
        self.assertEqual(sum(1 for p in limited if p[2] == 0), 3)

if __name__ == "__main__":
    unittest.main()
