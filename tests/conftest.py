import os

test_dir = os.path.dirname(__file__)
data_dir = os.path.join(test_dir, "script_folder", "data")
data_file = os.path.join(data_dir, "data")


def pytest_configure(config):
    os.makedirs(data_dir, exist_ok=True)
    if not os.path.exists(data_file):
        with open(data_file, "w") as f:
            f.write("test data\n")
