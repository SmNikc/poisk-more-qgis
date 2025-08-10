python def test_sitrep_data_complete(data): required = ["type", "datetime", "sru", "coords", "weather", "situation", "actions"] for field in required: assert field in data
