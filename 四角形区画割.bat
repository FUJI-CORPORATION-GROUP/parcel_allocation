@REM —v‘f“ü—Í
REM “¹‚É‰ˆ‚Á‚Ä•ªŠ„‚µ‚Ü‚·D
REM #jww
REM #cd
goto %1
REM #hmy—v‘f“ü—Íz |—v‘f“ü—Í|“¹˜Hì¬‚ ‚è|“¹˜Hì¬‚È‚µ|
REM #hc ƒƒjƒ…[‚ð‘I‘ð‚µ‚Ä‰º‚³‚¢B
REM #:1
REM #1-%d“¹˜H‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #2 “¹˜H‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #3-%d“¹˜H‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #4 “¹˜H‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #5-%d“¹˜H‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #6 “¹˜H‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #7-%d“¹˜H‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #8 “¹˜H‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #9-%d“¹˜H‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #10 “¹˜H‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #11-%d“¹˜H‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #12 “¹˜H‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #99#
REM #c ŠÔŒû –³Žw’è:7.6m/_/b
REM #c ‘î’n–ÊÏ –³Žw’è:100‡u/_/c
REM #hr
REM #e

@REM “¹˜HƒAƒŠŽw’è
REM #:2
REM #c “¹˜H• –³Žw’è:4m/_/a
REM #3-%d “¹‚ðì¬‚·‚é•Ó‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢D(L)free (R)Read
REM #4 “¹‚ðì¬‚·‚é•Ó‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢D(L)free (R)Read
REM #5-%dŠX‹æ‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #99#
REM #e

@REM “¹˜HƒiƒVŽw’è
REM #:3
REM #c ŠÔŒû‰ºŒÀ –³Žw’è:6.8m/_/a
REM #3-%dŠX‹æ‚ð‘I‘ð‚µ‚Ä‚­‚¾‚³‚¢.(L)free (R)Read
REM #99#
REM #e

@REM —v‘f“ü—Í
:1
copy jwc_temp.txt jwc_temp1.txt
echo "test"
python ŠO•”•ÏŒ`/parameter_in.py jwc_temp1.txt %2 %3
goto EXE-%1

@REM “¹˜HƒAƒŠŽw’è_ˆ—
:2
copy jwc_temp.txt jwc_temp2.txt
python ŠO•”•ÏŒ`/road_make.py jwc_temp2.txt %2
goto END

@REM “¹˜HƒiƒVŽw’è_ˆ—
:3
copy jwc_temp.txt jwc_temp2.txt
python ŠO•”•ÏŒ`/un_road_make.py jwc_temp2.txt %2
goto END

:END
python ŠO•”•ÏŒ`/split.py > jwc_temp.txt
@REM pause