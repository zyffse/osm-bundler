@echo off
set BIN_DIR=%~dp0\bin
set IMAGE_DIR=
IF NOT [%1]==[] set IMAGE_DIR=%1

FOR /f "tokens=*" %%G IN ('dir /b %IMAGE_DIR%\*.key') DO del /f /q %IMAGE_DIR%\%%G

FOR /f "tokens=*" %%G IN ('dir /b %IMAGE_DIR%\*.jpg') DO %BIN_DIR%\mogrify.exe -format pgm %IMAGE_DIR%\%%G
FOR /f "tokens=1 delims=." %%G IN ('dir /b %IMAGE_DIR%\*.pgm') DO %BIN_DIR%\siftWin32.exe < %IMAGE_DIR%\%%G.pgm > %IMAGE_DIR%\%%G.key
FOR /f "tokens=*" %%G IN ('dir /b %IMAGE_DIR%\*.pgm') DO del /f /q %IMAGE_DIR%\%%G

del /f /q list_keys.txt
FOR /f "tokens=*" %%G IN ('dir /b %IMAGE_DIR%\*.key') DO echo %IMAGE_DIR%\%%G>>list_keys.txt

del /f /q list_tmp.txt
FOR /f "tokens=*" %%G IN ('dir /b %IMAGE_DIR%\*.jpg') DO echo %%G>>list_tmp.txt
cscript %BIN_DIR%\extract_focal.vbs list_tmp.txt %IMAGE_DIR%
del /f /q list_tmp.txt
copy prepare\list.txt .\


%BIN_DIR%\KeyMatchFull.exe list_keys.txt matches.init.txt

mkdir bundle
del /f /q options.txt

echo --match_table matches.init.txt >> options.txt
echo --output bundle.out >> options.txt
echo --output_all bundle_ >> options.txt
echo --output_dir bundle >> options.txt
echo --variable_focal_length >> options.txt
echo --use_focal_estimate >> options.txt
echo --constrain_focal >> options.txt
echo --constrain_focal_weight 0.0001 >> options.txt
echo --estimate_distortion >> options.txt
echo --run_bundle >> options.txt

del /f /q constraints.txt
del /f /q pairwise_scores.txt

%BIN_DIR%\bundler.exe list.txt --options_file options.txt > bundle\out
FOR /f "tokens=*" %%G IN ('dir /b %IMAGE_DIR%\*.key') DO del /f /q %IMAGE_DIR%\%%G
echo [- Done -]