import pytest
from cpac.utils import traverse_deep


def test_traverse_deep():

    keys = lambda s: s.split('/')

    data = {
        'age': 54,
        'arms': ['arm1', 'arm2'],
        'legs': {
            'leg1': {
                'strength': 10,
                'feet': ['foot1'],
            },
            'leg2': {
                'strength': 12,
                'feet': ['foot1'],
            },
        }
    }

    age = traverse_deep(data, keys('age'))
    assert age == data['age']

    data = traverse_deep(data, keys('age'), 25)
    age = traverse_deep(data, keys('age'))
    assert age == 25

    arms = traverse_deep(data, keys('arms'))
    assert arms == ['arm1', 'arm2']

    data = traverse_deep(data, keys('arms/1'), 'arm3')
    arms = traverse_deep(data, keys('arms'))
    assert arms == ['arm1', 'arm3']

    data = traverse_deep(data, keys('legs/leg3'), {
        'strength': 45,
        'feet': ['foot1'],
    })

    legs_strength = traverse_deep(data, keys('legs/*/strength'))
    assert legs_strength == {'leg1': 10, 'leg2': 12, 'leg3': 45}