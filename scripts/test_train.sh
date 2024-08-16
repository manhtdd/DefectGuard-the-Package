#!bin/bash
defectguard -debug training -model deepjit -dg_save_folder . -repo_name javascript -repo_language JavaScript -device cuda -epochs 100;
defectguard -debug evaluating -model deepjit -dg_save_folder . -repo_name javascript -repo_language JavaScript -device cuda;
