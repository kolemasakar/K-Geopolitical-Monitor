#!/usr/bin/env python3
"""Fail-closed, offline OCI Always Free prerequisite checker for a NEW VPN VM.

No OCI API calls, credentials, account creation, charges or instance creation.
Inventory values MUST be verified manually in the destination tenancy Console.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def validate_inventory(data: dict) -> list[str]:
    errors: list[str] = []
    # Boolean fields must be explicitly present; unknown does not mean free.
    for field in ("tenancy_owner_authorized", "selected_shape_always_free",
                  "selected_image_always_free", "regional_capacity_confirmed",
                  "boot_volume_always_free", "public_ipv4_no_extra_charge",
                  "no_payg_upgrade", "no_nonfree_services"):
        if data.get(field) is not True:
            errors.append(f"{field}: explicit affirmative console verification required")
    home = data.get("home_region")
    region = data.get("deployment_region")
    if not isinstance(home, str) or not home.strip() or region != home:
        errors.append("Always Free compute MUST be in the verified tenancy home region")
    if data.get("egress_region_outside_ukraine") is not True:
        errors.append("Verify non-Ukraine egress region")
    try:
        storage_used = float(data["existing_boot_and_block_gb"])
    except (KeyError, TypeError, ValueError):
        errors.append("Existing tenancy boot+block storage in GB is required")
    else:
        if storage_used < 0 or storage_used + 50 > 200:
            errors.append("50 GB boot volume would exceed 200 GB Always Free combined storage")
    shape = data.get("selected_shape")
    if shape == "VM.Standard.E2.1.Micro":
        if not isinstance(data.get("existing_e2_micro_instances"), int):
            errors.append("Existing Always Free E2 Micro instance count is required")
        elif not 0 <= data["existing_e2_micro_instances"] < 2:
            errors.append("Two E2 Micro instances already consumed or invalid inventory")
    elif shape == "VM.Standard.A1.Flex":
        try:
            allocated_ocpu = float(data["existing_a1_ocpu"])
            allocated_ram = float(data["existing_a1_memory_gb"])
        except (KeyError, TypeError, ValueError):
            errors.append("Existing A1 OCPU and RAM allocations are required")
        else:
            if allocated_ocpu < 0 or allocated_ocpu + 1 > 2:
                errors.append("New 1-OCPU A1 VM exceeds 2 OCPU Always Free tenancy budget")
            if allocated_ram < 0 or allocated_ram + 2 > 12:
                errors.append("New 2-GB A1 VM exceeds 12 GB Always Free tenancy budget")
    else:
        errors.append("Only E2.1.Micro or A1.Flex with 1 OCPU/2 GB permitted")
    if data.get("existing_monthly_outbound_tenancy_tb_estimate") is None:
        errors.append("Tenancy-wide outbound data allowance must be audited")
    else:
        try:
            if not 0 <= float(data["existing_monthly_outbound_tenancy_tb_estimate"]) < 10:
                errors.append("10 TB/month shared Always Free outbound allowance exceeded")
        except (TypeError, ValueError):
            errors.append("Invalid outbound estimate")
    return errors


def main(path: str) -> int:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_inventory(data)
    print("OCI_NEW_VPN_VM_PREFLIGHT=" + ("PASS_TO_MANUAL_PROVISIONING_GATE" if not errors else "BLOCKED"))
    for err in errors:
        print("BLOCKER: " + err)
    print("NO_CLOUD_RESOURCE_CREATED=YES")
    return 0 if not errors else 2


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python3 oci_free_guard.py <locally-filled-inventory.json>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
