# this file is awkwardly named because it can't start with test_ or it will be picked up by pytest


def submit_indicator_datum(indicator_datum):
    """
    quick and dirty way to emulate an approved data-record
    does not create a submission meta-record
    """
    datum_version = indicator_datum.versions.last()
    datum_version.is_hso_submitted = True
    datum_version.is_program_submitted = True
    datum_version.save()
