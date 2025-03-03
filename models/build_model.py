from .FloatMLP import FloatMLP
from .QuantMLP import QuantMLP


def build_model(**kwargs):
    is_qat = kwargs.get("is_qat")
    if is_qat:
        return QuantMLP(**kwargs)
    else:
        return FloatMLP(**kwargs)
