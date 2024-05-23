#!bin/bash
defectguard -debug training -model lr -dg_save_folder . -repo_name javascript -repo_language JavaScript;
defectguard -debug evaluating -model lr -dg_save_folder . -repo_name javascript -repo_language JavaScript;
