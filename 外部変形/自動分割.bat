@REM 道に沿って分割します．
@REM #jww
@REM #hf
@REM #zs
@REM #zc
@REM #zz
@REM #zw
@REM #gn
@REM #1-%d 道を作成する辺を選択してください．(L)free (R)Read
@REM #2 道を作成する辺を選択してください．(L)free (R)Read
@REM #c道路幅 無指定:4000/_/a
@REM #c間口 無指定:7600/_/b
@REM #h1 道路を選択してください．
@REM #3-%d街区を指示して下さい．(L)free (R)Read
@REM #99#
@REM #hr
@REM #ht1
@REM #ht2
@REM #ht3
@REM #ht4
@REM #e
@copy jwc_temp.txt temp.txt > nul
@python 外部変形/random_split.py temp.txt %1 %2> jwc_temp.txt
@pause