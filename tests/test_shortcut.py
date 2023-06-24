import pytest
import functools
from mmodel import Model, BasicHandler
from mmodel.shortcut import modifier_shortcut


class TestModifierShorcut:
    @pytest.fixture
    def modifier(self):
        """Return a modifier function."""

        def mod(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs) + 1

            return wrapper

        return mod

    @pytest.fixture
    def model_instance(self, mmodel_G):
        """Return a model instance."""

        return Model("model", mmodel_G, BasicHandler)

    def test_modifier_name(self, model_instance):
        """Test if the modifier_shortcut changes model name."""

        new_model = modifier_shortcut(model_instance, {}, name="new_model")

        assert new_model.name == "new_model"

    def test_modifier_shortcut(self, model_instance, modifier):
        """Test modifier shortcut."""

        new_model = modifier_shortcut(
            model_instance, {"add": [modifier], "log": [modifier]}
        )

        assert new_model.graph.nodes["add"]["modifiers"][-1] == modifier
        assert new_model.graph.nodes["log"]["modifiers"][-1] == modifier

        assert new_model(9, 12, 12, 2) == (0, 2.0)

        # make sure the original graph is not modified

        assert model_instance.graph.nodes["add"]["modifiers"] == []
        assert model_instance.graph.nodes["log"]["modifiers"] == []
