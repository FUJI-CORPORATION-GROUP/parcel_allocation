@REM 要素入力
REM 道に沿って分割します．
REM #jww
REM #cd
goto %1
REM #hm【要素入力】 |要素入力|道路作成あり|道路作成なし|
REM #hc メニューを選択して下さい。
REM #:1
REM #1-%d道路を選択してください.(L)free (R)Read
REM #2 道路を選択してください.(L)free (R)Read
REM #3-%d道路を選択してください.(L)free (R)Read
REM #4 道路を選択してください.(L)free (R)Read
REM #5-%d道路を選択してください.(L)free (R)Read
REM #6 道路を選択してください.(L)free (R)Read
REM #7-%d道路を選択してください.(L)free (R)Read
REM #8 道路を選択してください.(L)free (R)Read
REM #9-%d道路を選択してください.(L)free (R)Read
REM #10 道路を選択してください.(L)free (R)Read
REM #11-%d道路を選択してください.(L)free (R)Read
REM #12 道路を選択してください.(L)free (R)Read
REM #99#
REM #c 間口 無指定:7.6m/_/b
REM #c 宅地面積 無指定:100�u/_/c
REM #hr
REM #e

@REM 道路アリ指定
REM #:2
REM #c 道路幅 無指定:4m/_/a
REM #3-%d 道を作成する辺を選択してください．(L)free (R)Read
REM #4 道を作成する辺を選択してください．(L)free (R)Read
REM #5-%d街区を選択してください.(L)free (R)Read
REM #99#
REM #e

@REM 道路ナシ指定
REM #:3
REM #c 間口下限 無指定:6.8m/_/a
REM #3-%d街区を選択してください.(L)free (R)Read
REM #99#
REM #e

@REM 要素入力
:1
copy jwc_temp.txt jwc_temp1.txt
echo "test"
python 外部変形/parameter_in.py jwc_temp1.txt %2 %3
goto EXE-%1

@REM 道路アリ指定_処理
:2
copy jwc_temp.txt jwc_temp2.txt
python 外部変形/road_make.py jwc_temp2.txt %2
goto END

@REM 道路ナシ指定_処理
:3
copy jwc_temp.txt jwc_temp2.txt
python 外部変形/un_road_make.py jwc_temp2.txt %2
goto END

:END
python 外部変形/split.py > jwc_temp.txt
@REM pause