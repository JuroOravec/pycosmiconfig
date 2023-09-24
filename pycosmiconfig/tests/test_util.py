from pycosmiconfig.port.util import get_property_by_path

source = {
    "ant": {
        "beetle": {
            "cootie": {
                "flea": "foo",
            },
            "louse": {
                "vermin": "bar",
            },
        },
        "fancy.name": {
            "another.fancy.name": 9,
        },
    },
    "ant.beetle.cootie": 333,
}


def describe_get_property_by_path():
    def test_property_name_includes_period():
        assert get_property_by_path(source, "ant.beetle.cootie") == 333

    def describe_period_delimited_string_path():
        def test_returns_defined_value():
            assert get_property_by_path(source, "ant") == source["ant"]
            assert get_property_by_path(source, "ant.beetle.cootie.flea") == "foo"
            assert (
                get_property_by_path(source, "ant.beetle.louse")
                == source["ant"]["beetle"]["louse"]
            )

        def test_returns_undefined():
            assert get_property_by_path(source, "beetle") is None
            assert get_property_by_path(source, "ant.beetle.cootie.fleeee") is None
            assert get_property_by_path(source, "ant.beetle.vermin") is None
            assert get_property_by_path(source, "ant.fancy.name") is None

    def describe_array_path():
        def test_returns_defined_value():
            assert get_property_by_path(source, ["ant"]) == source["ant"]
            assert (
                get_property_by_path(source, ["ant", "beetle", "cootie", "flea"])
                == "foo"
            )
            assert (
                get_property_by_path(source, ["ant", "beetle", "louse"])
                == source["ant"]["beetle"]["louse"]
            )

        def test_returns_undefined():
            assert get_property_by_path(source, ["beetle"]) is None
            assert (
                get_property_by_path(source, ["ant", "beetle", "cootie", "fleeee"])
                is None
            )
            assert get_property_by_path(source, ["ant", "beetle", "vermin"]) is None

        def test_handles_property_names_with_periods():
            assert (
                get_property_by_path(
                    source, ["ant", "fancy.name", "another.fancy.name"]
                )
                == 9
            )
            assert (
                get_property_by_path(
                    source, ["ant", "fancy.name", "another.fancy.name", "foo"]
                )
                is None
            )
            assert get_property_by_path(source, ["ant", "fancy.namez"]) is None
