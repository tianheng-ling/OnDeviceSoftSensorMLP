from torch.utils.data import DataLoader

from test import test
from hw_converter.convert2hw import convert2hw
from hw_estimation.hwsimulation import hwsimulation


def int_inference(
    test_dataloader: DataLoader,
    inference_dataloader: DataLoader,
    target_normalizer: object,
    model_params: dict,
    exp_config: dict,
):

    quant_model_params = model_params.copy()
    quant_model_params.update({"do_int_forward": True})

    test(
        model_params=quant_model_params,
        test_dataloader=test_dataloader,
        inference_dataloader=inference_dataloader,
        target_normalizer=target_normalizer,
        exp_config=exp_config,
    )

    # convert to hardware and simulate on different targets (xs15, ice40)
    target_hw_options = ["AMD", "Lattice"]
    for target_hw in target_hw_options:
        design = convert2hw(
            model_params=quant_model_params,
            exp_save_dir=exp_config["exp_save_dir"],
            target_hw=target_hw,
        )
        hwsimulation(exp_config["exp_save_dir"], design, target_hw=target_hw)
