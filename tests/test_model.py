import pytest
from mmodel.model import Model
from mmodel.handler import PlainHandler, H5Handler
from mmodel.modifier import loop_modifier
import math

MODEL_REPR = """test model
signature - a, d, f, b=2
returns - k, m
handler - PlainHandler
test object

long description"""

@pytest.fixture
def model_instance(mmodel_G):
    """Construct a model instance"""

    return Model(mmodel_G, PlainHandler)

def test_model_attr(model_instance, mmodel_signature):
    """Test the model has the correct name, signature, returns"""

    assert model_instance.__name__ == "test model"
    assert model_instance.__signature__ == mmodel_signature
    assert model_instance.returns == ['k', 'm']

def test_model_str(model_instance):
    """Test model representation"""

    assert str(model_instance) == MODEL_REPR

def test_execution(model_instance):
    """Test if the default is correctly used"""

    assert model_instance(10, 15, 20) == (-720, math.log(12, 2))
    assert model_instance(a=1, d=2, f=3, b=4) == (45, math.log(5, 4))

@pytest.fixture
def model_mod_instance(mmodel_G):
    """Construct a model instance"""

    loop_mod = loop_modifier('a')

    return Model(mmodel_G, PlainHandler, modifiers=[loop_mod])

def test_mod_attr(model_mod_instance):
    """Test if adding modifier changes the handler attribute (returns)"""

    assert model_mod_instance.returns == ['k', 'm']

def test_mod_execution(model_mod_instance):
    """Test if adding modifier changes the handler attribute (returns)"""

    assert model_mod_instance(a=[1, 2], b=2, d=3, f=4) == [(0, math.log(3, 2)), (16, 2)]

def test_mod_with_argument(mmodel_G):
    """Test if the handler arguments is correctly transferred"""

    h5model = Model(mmodel_G, H5Handler, handler_args={'h5_filename': 'test_file'})

    assert h5model.executor.h5_filename == 'test_file'


