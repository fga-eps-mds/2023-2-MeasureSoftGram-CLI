from pathlib import Path

import pytest

from src.cli.jsonReader import open_json_file
from src.cli.resources.measure import calculate_measures


def test_calculate_measures():
    json_data = open_json_file(
        Path(
            "tests/unit/data/fga-eps-mds-2022-2-MeasureSoftGram-CLI-01-05-2023-21-40-30-develop-extracted.msgram"
        )
    )

    infos, headers = calculate_measures(json_data)
    assert headers == ["Id", "Name", "Description", "Value", "Created at"]
    assert "measures" in infos

    measure_result = infos.get("measures")
    print(measure_result)
    measure_expected = [
        {"key": "passed_tests", "value": 1.0},
        {"key": "test_builds", "value": 0.9996329122628728},
        {"key": "test_coverage", "value": 0.4846666666666668},
        {"key": "non_complex_file_density", "value": 0.4603110903924873},
        {"key": "commented_file_density", "value": 0.03377777777777778},
        {"key": "duplication_absense", "value": 1.0},
    ]
    for measure_result, measure_expected in zip(measure_result, measure_expected):
        assert measure_result.get("key") == measure_expected.get("key")
        assert pytest.approx(measure_result.get("value")) == measure_expected.get(
            "value"
        )
