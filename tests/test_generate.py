from factory_boss.scripts.generate import main


def test_generate_does_not_raise():
    main()
    assert True, "if we reach this line then main() from generate did not raise"
