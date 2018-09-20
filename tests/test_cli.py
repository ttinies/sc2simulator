
from sc2simulator import cli


################################################################################
def test_parser():
    p = cli.optionsParser()
    assert bool(p)


################################################################################
def test_main():
    cli.main()
    assert True

