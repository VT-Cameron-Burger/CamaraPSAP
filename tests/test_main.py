"""Tests for main module."""

import pytest
from camarapsap.main import main


def test_main(capsys):
    """Test main function."""
    main()
    captured = capsys.readouterr()
    assert "Hello from CamaraPSAP!" in captured.out
