def test_package_importable():
    import movement_figures

    assert movement_figures.__doc__ is not None
