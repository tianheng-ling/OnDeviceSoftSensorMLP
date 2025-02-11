# quantization settings
quant_bits_options=(8) # 6 4)

# experiment settings
hidden_size_options=(10) # 30 60 120)
num_hidden_layers_options=(0) # 1 2 3) 

num_exps=1
# execute the script
for i in $(seq 1 $num_exps); do
    for hidden_size in "${hidden_size_options[@]}"; do
        for num_hidden_layers in "${num_hidden_layers_options[@]}"; do
            for quant_bits in "${quant_bits_options[@]}"; do
                exp_save_dir="experiments/quant/$hidden_size-hs/$num_hidden_layers-hl/$quant_bits-bit/"
                python main.py \
                    --hidden_size=$hidden_size --num_hidden_layers=$num_hidden_layers \
                    --quant_bits=$quant_bits --exp_save_dir=$exp_save_dir \
                    --is_quantized
            done
        done
    done
done