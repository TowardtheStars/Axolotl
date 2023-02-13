
import os
from os.path import join as joinpath

__all__ = ('data_root', 'annotation')

data_root = joinpath(os.getcwd(), 'AxolotlData')

def annotation(obj):
    return obj

