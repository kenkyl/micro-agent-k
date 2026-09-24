from micro_agent import __version__, cli


def test_version_flag(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["micro-agent", "--version"])
    cli.main()
    assert capsys.readouterr().out.strip() == f"micro-agent {__version__}"
