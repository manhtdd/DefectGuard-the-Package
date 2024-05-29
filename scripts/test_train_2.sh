#!bin/bash
defectguard -debug training -model simcom -dg_save_folder . -repo_name javascript -repo_language JavaScript -device cuda -epochs 30;
defectguard -debug evaluating -model simcom -dg_save_folder . -repo_name javascript -repo_language JavaScript -device cuda;
