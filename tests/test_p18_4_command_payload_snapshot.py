from kgeopolitical_monitor.shared_repository_concurrency import WriteCommand


def test_write_command_snapshots_payload_and_fingerprint_at_construction():
    source = {"nested": {"value": 1}, "items": [1, 2]}
    command = WriteCommand(
        object_type="event",
        object_id="obj-1",
        payload=source,
        idempotency_key="idem-1",
        expected_version=0,
    )

    payload_json = command.payload_json
    fingerprint = command.fingerprint

    source["nested"]["value"] = 999
    source["items"].append(3)
    source["new"] = True

    assert command.payload_json == payload_json
    assert command.fingerprint == fingerprint
    assert command.payload_json == '{"items":[1,2],"nested":{"value":1}}'
