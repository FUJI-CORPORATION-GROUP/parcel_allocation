@REM ���ɉ����ĕ������܂��D
@REM #jww
@REM #hf
@REM #zs
@REM #zc
@REM #zz
@REM #zw
@REM #gn
@REM #1-%d �����쐬����ӂ�I�����Ă��������D(L)free (R)Read
@REM #2 �����쐬����ӂ�I�����Ă��������D(L)free (R)Read
@REM #c���H�� ���w��:4000/_/a
@REM #c�Ԍ� ���w��:7600/_/b
@REM #h1 ���H��I�����Ă��������D
@REM #3-%d�X����w�����ĉ������D(L)free (R)Read
@REM #99#
@REM #hr
@REM #ht1
@REM #ht2
@REM #ht3
@REM #ht4
@REM #e
@copy jwc_temp.txt temp.txt > nul
@python �O���ό`/random_split.py temp.txt %1 %2> jwc_temp.txt
@pause