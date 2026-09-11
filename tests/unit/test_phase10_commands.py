"""Unit tests for dashboard/commands/commands.py."""

import pytest
from smriti.core.models import WorkspaceType
from smriti.dashboard.commands.commands import (
    ActivateWorkspaceCommand,
    ApplyFilterCommand,
    CompareCommand,
    ExportCommand,
    SelectClaimCommand,
    SetPageCommand,
    SetSortCommand,
    SubmitSearchCommand,
)


def test_select_claim_command_is_immutable():
    cmd = SelectClaimCommand(session_id="s1", claim_id="c001")
    with pytest.raises(Exception):
        cmd.claim_id = "c002"


def test_activate_workspace_command_carries_workspace_type():
    cmd = ActivateWorkspaceCommand(
        session_id="s1",
        workspace_type=WorkspaceType.AUDIT,
    )
    assert cmd.workspace_type == WorkspaceType.AUDIT


def test_compare_command_carries_claim_ids():
    cmd = CompareCommand(session_id="s1", claim_ids=("c001", "c002"))
    assert "c001" in cmd.claim_ids
    assert "c002" in cmd.claim_ids


def test_apply_filter_command_carries_field_and_value():
    cmd = ApplyFilterCommand(session_id="s1", field="calibration_label", value="high")
    assert cmd.field == "calibration_label"
    assert cmd.value == "high"


def test_submit_search_command_carries_query():
    cmd = SubmitSearchCommand(session_id="s1", query="neural network")
    assert cmd.query == "neural network"


def test_export_command_carries_format():
    cmd = ExportCommand(session_id="s1", format="csv")
    assert cmd.format == "csv"


def test_set_page_command_carries_page():
    cmd = SetPageCommand(session_id="s1", page=3)
    assert cmd.page == 3


def test_set_sort_command_carries_sort_args():
    cmd = SetSortCommand(session_id="s1", sort_field="uncertainty_score", sort_order="asc")
    assert cmd.sort_field == "uncertainty_score"
    assert cmd.sort_order == "asc"
