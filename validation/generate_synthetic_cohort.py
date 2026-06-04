"""
Generate synthetic patient cohort with known ground truth for validation.

Covers:
- 50 synthetic patients
- Multiple tumor types (NSCLC, HGSOC, breast, glioma, CRC)
- Variant types: pathogenic, LP + germline, VUS
- Complete ground truth annotations
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def create_pathogenic_variant(gene: str, variant: str, hgvs_p: str, tier: str = "Tier 1") -> Dict[str, Any]:
    """Create a pathogenic variant with ground truth."""
    return {
        "gene": gene,
        "hgvs_p": hgvs_p,
        "consequence": "missense_variant",
        "vaf": 0.40,
        "ground_truth": {
            "clinical_significance": "Pathogenic",
            "oncological_relevance": "High",
            "evidence_tier": tier,
            "mechanism": f"{gene} {variant} activating/loss-of-function mutation",
            "germline": False,
        },
    }


def create_germline_variant(gene: str, variant: str, hgvs_p: str, syndrome: str) -> Dict[str, Any]:
    """Create a germline pathogenic variant."""
    return {
        "gene": gene,
        "hgvs_p": hgvs_p,
        "consequence": "frameshift_variant",
        "vaf": 0.50,
        "ground_truth": {
            "clinical_significance": "Pathogenic",
            "oncological_relevance": "High",
            "evidence_tier": "Tier 1",
            "mechanism": f"{syndrome} syndrome - loss of DNA repair",
            "germline": True,
            "syndrome": syndrome,
        },
    }


def create_vus_variant(gene: str, variant: str, hgvs_p: str) -> Dict[str, Any]:
    """Create a VUS (variant of uncertain significance)."""
    return {
        "gene": gene,
        "hgvs_p": hgvs_p,
        "consequence": "missense_variant",
        "vaf": 0.30,
        "ground_truth": {
            "clinical_significance": "VUS",
            "oncological_relevance": "Unknown",
            "evidence_tier": "Tier 4",
            "mechanism": "Unknown - insufficient evidence",
            "germline": False,
            "notes": "Recommend functional studies",
        },
    }


def generate_cohort(num_patients: int = 50) -> List[Dict[str, Any]]:
    """Generate synthetic cohort with ground truth."""
    cohort = []

    # NSCLC patients (15)
    for i in range(1, 6):
        cohort.append({
            "patient_id": f"SYN_{i:03d}",
            "tumor_type": "Non-small cell lung adenocarcinoma",
            "variants": [create_pathogenic_variant("EGFR", "L858R", "p.L858R")],
            "expected_tarvia_variant_gate": "PASS",
        })

    for i in range(6, 11):
        cohort.append({
            "patient_id": f"SYN_{i:03d}",
            "tumor_type": "NSCLC",
            "variants": [create_pathogenic_variant("KRAS", "G12C", "p.G12C")],
            "expected_tarvia_variant_gate": "PASS",
        })

    for i in range(11, 16):
        cohort.append({
            "patient_id": f"SYN_{i:03d}",
            "tumor_type": "NSCLC",
            "variants": [create_pathogenic_variant("ALK", "fusion", "p.Fusion", "Tier 1")],
            "expected_tarvia_variant_gate": "PASS",
        })

    # HGSOC patients (10)
    for i in range(16, 21):
        cohort.append({
            "patient_id": f"SYN_{i:03d}",
            "tumor_type": "High-grade serous ovarian cancer",
            "variants": [create_pathogenic_variant("TP53", "R175H", "p.R175H", "Tier 2")],
            "expected_tarvia_variant_gate": "PASS",
        })

    for i in range(21, 26):
        cohort.append({
            "patient_id": f"SYN_{i:03d}",
            "tumor_type": "HGSOC",
            "variants": [create_germline_variant("BRCA2", "6174delT", "p.Phe1794fs*7", "HBOC")],
            "expected_tarvia_variant_gate": "PASS",
        })

    # Breast cancer patients (10)
    for i in range(26, 31):
        cohort.append({
            "patient_id": f"SYN_{i:03d}",
            "tumor_type": "Hormone receptor positive breast cancer",
            "variants": [create_pathogenic_variant("PIK3CA", "E545K", "p.E545K")],
            "expected_tarvia_variant_gate": "PASS",
        })

    for i in range(31, 36):
        cohort.append({
            "patient_id": f"SYN_{i:03d}",
            "tumor_type": "Breast cancer",
            "variants": [create_germline_variant("BRCA1", "5382insC", "p.Trp1797fs*1", "HBOC")],
            "expected_tarvia_variant_gate": "PASS",
        })

    # Glioma patients (5)
    for i in range(36, 41):
        cohort.append({
            "patient_id": f"SYN_{i:03d}",
            "tumor_type": "Glioblastoma",
            "variants": [create_pathogenic_variant("IDH1", "R132H", "p.R132H")],
            "expected_tarvia_variant_gate": "PASS",
        })

    # CRC patients (10)
    for i in range(41, 46):
        cohort.append({
            "patient_id": f"SYN_{i:03d}",
            "tumor_type": "Colorectal cancer",
            "variants": [create_pathogenic_variant("BRAF", "V600E", "p.V600E")],
            "expected_tarvia_variant_gate": "PASS",
        })

    for i in range(46, 51):
        cohort.append({
            "patient_id": f"SYN_{i:03d}",
            "tumor_type": "CRC",
            "variants": [create_vus_variant("PTEN", "novel", "p.L233P")],
            "expected_tarvia_variant_gate": "FAIL",  # VUS → lower confidence
        })

    return cohort[:num_patients]


def main():
    """Generate and save synthetic cohort."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic patient cohort")
    parser.add_argument("--num-patients", type=int, default=50)
    parser.add_argument("--output", type=Path, default=Path("validation/cohorts/synthetic_50_patients.json"))
    args = parser.parse_args()

    log.info(f"Generating {args.num_patients} synthetic patients...")
    cohort = generate_cohort(args.num_patients)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(cohort, f, indent=2)

    log.info(f"Cohort saved to: {args.output}")
    log.info(f"Summary:")
    log.info(f"  Total patients: {len(cohort)}")
    log.info(f"  Expected PASS gate: {sum(1 for p in cohort if p.get('expected_tarvia_variant_gate') == 'PASS')}")
    log.info(f"  Expected FAIL gate: {sum(1 for p in cohort if p.get('expected_tarvia_variant_gate') == 'FAIL')}")


if __name__ == "__main__":
    main()
