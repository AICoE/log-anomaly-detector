from fact_store.app import FactStore

METADATA_FILE = "factstore.parquet"


def test_duplicate_input():
    """
    Validating if user gives us duplicate input and check if input is in
    the set, let Bloom filter data structure to check without looping
    through dataset for duplicates

    We will attempt to simulate a user inputing duplicate ids

    Inserting : id = f5eb1d86
    Inserting : id = f5eb1d86

    Should result in function returning False

    :return:
    """
    fs = FactStore(feedback_metadata=METADATA_FILE)
    fs.write_feedback("f5eb1d86", "Yes")
    assert fs.write_feedback("f5eb1d86", "Yes") is False


def test_nonduplicate_input():
    """
    Validating if user gives us not in the set. Let Bloom filter data
    structure to check without looping through dataset
    for duplicates

    We will attempt to simulate a user inputing duplicate ids

    Inserting : id = a12345A
    Inserting : id = bcderrZ

    Should result in function returning True when it has successfully inserted
    into the bloom filter.

    :return:
    """
    fs = FactStore(feedback_metadata=METADATA_FILE)
    fs.write_feedback("a12345A", "Yes")
    assert fs.write_feedback("bcderrZ", "Yes") is True


def test_reading_input():
    """
    Testing after the tests above write to file that the
    right values exist in the file.
    :return:
    """
    fs = FactStore(feedback_metadata=METADATA_FILE)
    df = fs.readall_feedback()
    assert df.id[0] == "f5eb1d86"
    assert df.id[1] == "a12345A"
    assert df.id[2] == "bcderrZ"
