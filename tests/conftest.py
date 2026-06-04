"""
Pytest configuration and fixtures for TARVIA validation tests.
"""
import pytest
import json
from pathlib import Path
import tempfile


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for test artifacts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_vcf():
    """Sample VCF content with known variants."""
    return """##fileformat=VCFv4.2
##INFO=<ID=ANN,Number=.,Type=String,Description="Annotation from SnpEff">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
chr7	55259515	.	T	A	100	PASS	ANN=A|missense_variant|MODERATE|EGFR|ENSG00000146884|transcript|ENST00000275493|protein_coding|21/28|c.2573T>A|p.L858R|2573/7512|1858/2507|620/835	GT:DP:AF	0/1:100:0.45
chr12	25245350	.	G	A	100	PASS	ANN=A|missense_variant|HIGH|KRAS|ENSG00000133703|transcript|ENST00000311936|protein_coding|2/4|c.35G>A|p.G12D|35/6557|12/2185|12/728	GT:DP:AF	0/1:80:0.50
"""


@pytest.fixture
def sample_variant_json():
    """Sample parsed variant JSON."""
    return [
        {
            "variant_id": "chr7_55259515_T_A",
            "gene": "EGFR",
            "hgvs_p": "p.L858R",
            "hgvs_c": "c.2573T>A",
            "consequence": "missense_variant",
            "impact": "MODERATE",
            "vaf": 0.45,
            "depth": 100,
        },
        {
            "variant_id": "chr12_25245350_G_A",
            "gene": "KRAS",
            "hgvs_p": "p.G12D",
            "hgvs_c": "c.35G>A",
            "consequence": "missense_variant",
            "impact": "HIGH",
            "vaf": 0.50,
            "depth": 80,
        },
    ]


@pytest.fixture
def sample_interpretation():
    """Sample variant interpretation from Claude."""
    return [
        {
            "variant_id": "chr7_55259515_T_A",
            "gene": "EGFR",
            "clinical_significance": "Pathogenic",
            "oncological_relevance": "High",
            "evidence_tier": "Tier 1",
            "cancer_types": ["NSCLC"],
            "mechanism": "Activating mutation in kinase domain",
            "targeted_therapies": ["Osimertinib"],
            "germline_implications": False,
            "interpretation_summary": "EGFR L858R is a well-established sensitizing mutation.",
            "confidence": "High",
        }
    ]


@pytest.fixture
def sample_gate_decision():
    """Sample TARVIA gate decision."""
    return {
        "gate": "variant_interpretation",
        "score": 87.3,
        "threshold": 80.0,
        "decision": "PASS",
        "action": "Generate clinical report",
    }


@pytest.fixture
def synthetic_patient():
    """Sample synthetic patient with ground truth."""
    return {
        "patient_id": "SYN_001",
        "tumor_type": "NSCLC adenocarcinoma",
        "variants": [
            {
                "gene": "EGFR",
                "hgvs_p": "p.L858R",
                "consequence": "missense_variant",
                "vaf": 0.45,
                "ground_truth": {
                    "clinical_significance": "Pathogenic",
                    "oncological_relevance": "High",
                    "evidence_tier": "Tier 1",
                    "targeted_therapies": ["Osimertinib"],
                    "germline": False,
                    "notes": "Standard EGFR sensitizing mutation",
                },
            }
        ],
        "expected_tarvia_variant_gate": "PASS",
        "expected_tarvia_structure_gate": "N/A",
    }


def pytest_addoption(parser):
    """Add custom pytest options."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests (requires API keys)",
    )


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires API keys)"
    )


def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless --integration flag."""
    if config.getoption("--integration"):
        return

    skip_integration = pytest.mark.skip(reason="need --integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
