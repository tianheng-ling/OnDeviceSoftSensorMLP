from .FloatMLP import FloatMLP
from .QuantMLP import QuantMLP


def build_model(**kwargs):
    is_quantized = kwargs.get("is_quantized")
    if is_quantized:
        return QuantMLP(**kwargs)
    else:
        return FloatMLP(**kwargs)
