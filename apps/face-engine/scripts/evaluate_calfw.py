"""
CALFW Evaluation Pipeline

Evaluates the exact Picaxe Face Engine on the CALFW dataset.
"""

import os
import sys
import argparse
import time
import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Any

import cv2
import numpy as np
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("Warning: matplotlib not installed. Plot generation will be skipped.")
    MATPLOTLIB_AVAILABLE = False

# Ensure the app directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.detection.detector import detect_faces, _get_insightface_app
from app.embedding.insightface import InsightFaceEmbedder
from app.embedding.model import cosine_similarity
from app.core.config import settings

def parse_args():
    args_parser = argparse.ArgumentParser(description="CALFW Benchmark for Picaxe Face Engine")
    args_parser.add_argument("--dataset-root", type=str, default=os.getenv("CALFW_ROOT"), help="Path to CALFW dataset root directory.")
    args_parser.add_argument("--cache-dir", type=str, default=None, help="Path to store/load embedding cache.")
    args_parser.add_argument("--force-recompute", action="store_true", help="Force recomputation of embeddings ignoring cache.")
    args_parser.add_argument("--max-pairs", type=int, default=None, help="Maximum number of verification pairs to evaluate.")
    
    return args_parser.parse_args()


def load_pairs(pairs_file: Path) -> List[Tuple[str, str, int]]:
    """
    Parses pairs_CALFW.txt
    Returns a list of tuples: (image1_name, image2_name, label)
    where label=1 for same, label=0 for different.
    """
    if not pairs_file.exists():
        raise FileNotFoundError(f"Pairs file not found at {pairs_file}")

    with open(pairs_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) % 2 != 0:
        raise ValueError(f"Expected an even number of lines in pairs file, got {len(lines)}")

    pairs = []
    for i in range(0, len(lines), 2):
        parts1 = lines[i].split()
        parts2 = lines[i+1].split()
        
        if len(parts1) != 2 or len(parts2) != 2:
            raise ValueError(f"Invalid format at lines {i+1}-{i+2}")
            
        img1, label1 = parts1[0], int(parts1[1])
        img2, label2 = parts2[0], int(parts2[1])
        
        if label1 != label2:
            raise ValueError(f"Inconsistent labels within pair at lines {i+1}-{i+2}: {label1} vs {label2}")
            
        norm_label = 1 if label1 > 0 else 0
        pairs.append((img1, img2, norm_label))
        
    return pairs

def validate_args(args):
    """Validates parsed arguments."""
    if not args.dataset_root:
        raise ValueError("--dataset-root or CALFW_ROOT environment variable must be provided.")
    if args.max_pairs is not None and args.max_pairs <= 0:
        raise ValueError("--max-pairs must be greater than 0.")

def limit_pairs(pairs: List[Tuple[str, str, int]], max_pairs: int) -> List[Tuple[str, str, int]]:
    """Limits the number of pairs if max_pairs is provided, aiming for a balanced positive/negative subset."""
    if max_pairs is None:
        return pairs
    
    pos_pairs = [p for p in pairs if p[2] == 1]
    neg_pairs = [p for p in pairs if p[2] == 0]
    
    # Base targets: half positive, half negative. Extra to positive if odd.
    target_pos = (max_pairs + 1) // 2
    target_neg = max_pairs // 2
    
    # Adjust if there are fewer available than the target
    if len(pos_pairs) < target_pos:
        target_neg = min(len(neg_pairs), target_neg + (target_pos - len(pos_pairs)))
        target_pos = len(pos_pairs)
    elif len(neg_pairs) < target_neg:
        target_pos = min(len(pos_pairs), target_pos + (target_neg - len(neg_pairs)))
        target_neg = len(neg_pairs)
        
    return pos_pairs[:target_pos] + neg_pairs[:target_neg]

def get_image_embedding(image_path: Path, embedder: InsightFaceEmbedder) -> Tuple[np.ndarray, str]:
    """
    Loads an image, detects the face, and returns its 512-D embedding.
    Returns: (embedding, failure_reason_if_any)
    """
    if not image_path.exists():
        return None, "Missing image file"

    # Read with OpenCV
    img_bgr = cv2.imread(str(image_path))
    if img_bgr is None:
        return None, "Unreadable image"

    # Convert to RGB
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    try:
        faces = detect_faces(img_rgb)
    except Exception as e:
        return None, f"Detection failed: {str(e)}"

    if len(faces) == 0:
        return None, "No detectable face"

    reason = None
    if len(faces) > 1:
        # We record the ambiguity but use the highest confidence face (sorted by detector)
        reason = "Multiple detected faces, used highest confidence"
    
    try:
        embedding = embedder.embed_face(faces[0].raw_face_obj)
        return embedding, reason
    except Exception as e:
        return None, f"Embedding failed: {str(e)}"

def compute_metrics(similarities: List[float], labels: List[int], thresholds: List[float]) -> List[Dict[str, Any]]:
    results = []
    sims = np.array(similarities)
    lbls = np.array(labels)
    
    for th in thresholds:
        preds = (sims >= th).astype(int)
        
        tp = np.sum((preds == 1) & (lbls == 1))
        tn = np.sum((preds == 0) & (lbls == 0))
        fp = np.sum((preds == 1) & (lbls == 0))
        fn = np.sum((preds == 0) & (lbls == 1))
        
        total = len(lbls)
        accuracy = (tp + tn) / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
        
        results.append({
            "threshold": th,
            "tp": int(tp),
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "fpr": float(fpr),
            "fnr": float(fnr)
        })
        
    return results

def plot_score_distribution(sims_pos: List[float], sims_neg: List[float], output_path: Path):
    plt.figure(figsize=(10, 6))
    plt.hist(sims_pos, bins=50, alpha=0.7, label='Same Identity (Positives)', density=True)
    plt.hist(sims_neg, bins=50, alpha=0.7, label='Different Identity (Negatives)', density=True)
    plt.title('CALFW Cosine Similarity Distribution')
    plt.xlabel('Cosine Similarity')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def main():
    args = parse_args()
    try:
        validate_args(args)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    dataset_root = Path(args.dataset_root)
    pairs_file = dataset_root / "pairs_CALFW.txt"
    images_dir = dataset_root / "aligned images"
    
    if not images_dir.exists():
        print(f"Error: Aligned images directory not found at {images_dir}")
        sys.exit(1)
        
    output_dir = Path(__file__).parent / "evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 50)
    print("CALFW Benchmark Evaluation")
    print("=" * 50)
    print(f"Dataset root: {dataset_root}")
    
    # 1. Parse pairs
    print("Parsing pairs...")
    pairs = load_pairs(pairs_file)
    total_available = len(pairs)
    pos_available = sum(1 for p in pairs if p[2] == 1)
    neg_available = sum(1 for p in pairs if p[2] == 0)
    
    assert pos_available + neg_available == total_available, "Positive and negative pair counts must sum up to total available pairs."
    
    pairs = limit_pairs(pairs, args.max_pairs)
    
    pos_selected = sum(1 for p in pairs if p[2] == 1)
    neg_selected = sum(1 for p in pairs if p[2] == 0)
    
    print(f"Total pairs available: {total_available}")
    print(f"Positive pairs available: {pos_available}")
    print(f"Negative pairs available: {neg_available}")
    print(f"Pairs selected: {len(pairs)}")
    print(f"Positive pairs selected: {pos_selected}")
    print(f"Negative pairs selected: {neg_selected}")
    
    unique_images = set()
    for p1, p2, _ in pairs:
        unique_images.add(p1)
        unique_images.add(p2)
    print(f"Total unique images: {len(unique_images)}")
    
    # 2. Setup caching
    embeddings_cache = {}
    cache_file = None
    if args.cache_dir:
        cache_path = Path(args.cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        cache_file = cache_path / "embeddings_cache.npz"
        
        if cache_file.exists() and not args.force_recompute:
            print(f"Loading cache from {cache_file}...")
            npz = np.load(cache_file)
            embeddings_cache = {name: npz[name] for name in npz.files}
            print(f"Loaded {len(embeddings_cache)} embeddings from cache.")

    # 3. Initialize model
    print("Initializing Face Engine...")
    start_init = time.time()
    # Loading models once via existing singleton
    _get_insightface_app()
    embedder = InsightFaceEmbedder()
    init_time = time.time() - start_init
    print(f"Model initialized in {init_time:.2f}s.")
    
    # 4. Generate/Load Embeddings
    print("Processing unique images...")
    failed_images = {}
    ambiguous_images = {}
    
    start_emb = time.time()
    processed_count = 0
    for img_name in unique_images:
        if img_name in embeddings_cache:
            continue
            
        emb, reason = get_image_embedding(images_dir / img_name, embedder)
        
        if emb is None:
            failed_images[img_name] = reason
        else:
            embeddings_cache[img_name] = emb
            if reason:
                ambiguous_images[img_name] = reason
                
        processed_count += 1
        if processed_count % 500 == 0:
            print(f"Processed {processed_count}/{len(unique_images) - len(embeddings_cache)} newly loaded images.")
            
    emb_time = time.time() - start_emb
    print(f"Total embedding time: {emb_time:.2f}s (Avg: {emb_time/processed_count if processed_count > 0 else 0:.4f}s per new image)")
    
    if cache_file and (args.force_recompute or processed_count > 0):
        print("Saving cache...")
        np.savez_compressed(cache_file, **embeddings_cache)
        
    # 5. Evaluate Pairs
    print("Evaluating pairs...")
    start_eval = time.time()
    similarities = []
    labels = []
    skipped_pairs = 0
    
    pos_sims = []
    neg_sims = []
    
    for img1, img2, label in pairs:
        if img1 in failed_images or img2 in failed_images:
            skipped_pairs += 1
            continue
            
        emb1 = embeddings_cache[img1]
        emb2 = embeddings_cache[img2]
        
        sim = cosine_similarity(emb1, emb2)
        similarities.append(sim)
        labels.append(label)
        
        if label == 1:
            pos_sims.append(sim)
        else:
            neg_sims.append(sim)
            
    eval_time = time.time() - start_eval
    print(f"Evaluated {len(similarities)} pairs in {eval_time:.2f}s")
    print(f"Skipped {skipped_pairs} pairs due to failed image processing.")
    
    # 6. Compute Threshold Metrics
    thresholds = [float(f"{i/100:.2f}") for i in range(30, 96, 5)]
    results = compute_metrics(similarities, labels, thresholds)
    
    # 7. Generate outputs
    # JSON
    model_info = {
        "detector": settings.DETECTOR_MODEL_NAME,
        "recognition": settings.RECOGNITION_MODEL_NAME,
        "embedding_dimension": settings.EMBEDDING_DIMENSION,
        "similarity_metric": settings.DISTANCE_METRIC
    }
    
    best_threshold_result = max(results, key=lambda x: x["accuracy"])
    # Recommend a threshold focusing on low FPR but maintaining decent recall (for Picaxe use case)
    # Target FPR < 0.001 or as low as possible while keeping F1 high
    recommended_threshold = None
    for res in sorted(results, key=lambda x: x["threshold"]):
        if res["fpr"] <= 0.01:
            recommended_threshold = res
            break
    if not recommended_threshold:
        recommended_threshold = best_threshold_result
    
    report_data = {
        "dataset": "CALFW",
        "total_pairs": len(pairs),
        "evaluated_pairs": len(similarities),
        "positive_pairs": len(pos_sims),
        "negative_pairs": len(neg_sims),
        "skipped_pairs": skipped_pairs,
        "unique_images": len(unique_images),
        "failed_images": failed_images,
        "ambiguous_images": ambiguous_images,
        "model_info": model_info,
        "recommended_threshold": recommended_threshold,
        "best_accuracy_threshold": best_threshold_result,
        "timing": {
            "initialization_time_s": init_time,
            "total_embedding_time_s": emb_time,
            "total_pair_evaluation_time_s": eval_time
        }
    }
    
    json_path = output_dir / "calfw_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=4)
        
    # CSV
    csv_path = output_dir / "calfw_thresholds.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        
    # Plot
    if MATPLOTLIB_AVAILABLE:
        plot_path = output_dir / "calfw_score_distribution.png"
        plot_score_distribution(pos_sims, neg_sims, plot_path)
    else:
        plot_path = "Skipped (matplotlib not installed)"
    
    # Markdown
    md_path = output_dir / "calfw_report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# CALFW Evaluation Report\n\n")
        f.write("## Dataset Information\n")
        f.write(f"- **Total Pairs**: {len(pairs)}\n")
        f.write(f"- **Evaluated Pairs**: {len(similarities)}\n")
        f.write(f"- **Skipped Pairs**: {skipped_pairs}\n")
        f.write(f"- **Unique Images**: {len(unique_images)}\n")
        f.write(f"- **Failed Images**: {len(failed_images)}\n\n")
        
        f.write("## Model Information\n")
        f.write(f"- **Detector**: {settings.DETECTOR_MODEL_NAME}\n")
        f.write(f"- **Recognition Model**: {settings.RECOGNITION_MODEL_NAME}\n")
        f.write(f"- **Embedding Dimension**: {settings.EMBEDDING_DIMENSION}\n")
        f.write(f"- **Similarity Metric**: {settings.DISTANCE_METRIC}\n\n")
        
        f.write("## Best Accuracy Threshold\n")
        f.write(f"- **Threshold**: {best_threshold_result['threshold']}\n")
        f.write(f"- **Accuracy**: {best_threshold_result['accuracy']:.4f}\n")
        f.write(f"- **FPR**: {best_threshold_result['fpr']:.4f}\n\n")
        
        f.write("## Recommended Threshold (Optimized for Picaxe Production)\n")
        f.write("*Note: This is the recommended operating threshold for this evaluation dataset, prioritizing precision and minimizing false positives.*\n")
        f.write(f"- **Threshold**: {recommended_threshold['threshold']}\n")
        f.write(f"- **Precision**: {recommended_threshold['precision']:.4f}\n")
        f.write(f"- **Recall**: {recommended_threshold['recall']:.4f}\n")
        f.write(f"- **F1 Score**: {recommended_threshold['f1']:.4f}\n")
        f.write(f"- **False Positives**: {recommended_threshold['fp']}\n")
        f.write(f"- **FPR**: {recommended_threshold['fpr']:.4f}\n\n")
        
        if failed_images:
            f.write("## Failed Images\n")
            for img, reason in list(failed_images.items())[:50]:
                f.write(f"- `{img}`: {reason}\n")
            if len(failed_images) > 50:
                f.write(f"- *... and {len(failed_images) - 50} more*\n")

    print("\nEvaluation complete! Artifacts generated:")
    print(f"- JSON: {json_path}")
    print(f"- CSV:  {csv_path}")
    print(f"- PNG:  {plot_path}")
    print(f"- MD:   {md_path}")
    
if __name__ == "__main__":
    main()
