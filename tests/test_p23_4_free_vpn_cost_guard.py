"""Strict offline budget gate for a separate, free OCI VPN relay node."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "oci_free_guard", ROOT / "ops/p23_4_govru_free_vpn/oci_free_guard.py"
)
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


def eligible_inventory():
    return {
        "tenancy_owner_authorized": True,
        "home_region": "eu-frankfurt-1",
        "deployment_region": "eu-frankfurt-1",
        "egress_region_outside_ukraine": True,
        "selected_shape": "VM.Standard.E2.1.Micro",
        "selected_shape_always_free": True,
        "selected_image_always_free": True,
        "regional_capacity_confirmed": True,
        "existing_e2_micro_instances": 0,
        "existing_boot_and_block_gb": 50,
        "boot_volume_always_free": True,
        "public_ipv4_no_extra_charge": True,
        "existing_monthly_outbound_tenancy_tb_estimate": 0.01,
        "no_payg_upgrade": True,
        "no_nonfree_services": True,
    }


def test_micro_sample_passes_only_verified_zero_cost_inventory():
    assert guard.validate_inventory(eligible_inventory()) == []


def test_unverified_fields_and_cross_region_fail_closed():
    data = eligible_inventory()
    data.update(home_region=None, deployment_region="eu-frankfurt-1",
                selected_shape_always_free=None, regional_capacity_confirmed=False)
    assert len(guard.validate_inventory(data)) >= 3


def test_exhausted_free_micro_or_boot_storage_blocks():
    data = eligible_inventory()
    data["existing_e2_micro_instances"] = 2
    assert guard.validate_inventory(data)
    data = eligible_inventory()
    data["existing_boot_and_block_gb"] = 151
    assert guard.validate_inventory(data)


def test_trial_credit_and_nonfree_resources_do_not_substitute():
    data = eligible_inventory()
    data["no_payg_upgrade"] = False
    data["no_nonfree_services"] = False
    assert len(guard.validate_inventory(data)) >= 2


def test_fallback_a1_is_at_most_one_ocpu_two_gb():
    data = eligible_inventory()
    data.update(selected_shape="VM.Standard.A1.Flex", existing_a1_ocpu=1,
                existing_a1_memory_gb=10)
    assert guard.validate_inventory(data) == []
    data["existing_a1_memory_gb"] = 11
    assert guard.validate_inventory(data)


def test_external_ipv4_and_egress_budget_must_be_verified():
    data = eligible_inventory()
    data.update(public_ipv4_no_extra_charge=False,
                existing_monthly_outbound_tenancy_tb_estimate=None)
    assert len(guard.validate_inventory(data)) >= 2
