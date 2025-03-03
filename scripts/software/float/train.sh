# model settings
hidden_size_options=(10) # 20 30) 
num_hidden_layers_options=(0) # 1 2)

# experiment settings
num_exps=1

for i in $(seq 1 $num_exps); do
    for hidden_size in "${hidden_size_options[@]}"; do
        for num_hidden_layers in "${num_hidden_layers_options[@]}"; do
                exp_base_save_dir="experiments/float/$hidden_size-hs/$num_hidden_layers-hl/"
                python main.py \
                    --hidden_size=$hidden_size --num_hidden_layers=$num_hidden_layers \
                    --exp_base_save_dir=$exp_base_save_dir
        done
    done
done