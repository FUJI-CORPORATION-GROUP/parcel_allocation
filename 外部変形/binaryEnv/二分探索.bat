@REM �v�f����
REM ���ɉ����ĕ������܂��D
REM #jww
REM #cd
goto %1
REM #hm�y�v�f���́z |���H�I��|�X��I��|
REM #hc ���j���[��I�����ĉ������B
REM #:1
REM #1-%d���H��I�����Ă�������.(L)free (R)Read
REM #2 ���H��I�����Ă�������.(L)free (R)Read
REM #3-%d���H��I�����Ă�������.(L)free (R)Read
REM #4 ���H��I�����Ă�������.(L)free (R)Read
REM #5-%d���H��I�����Ă�������.(L)free (R)Read
REM #6 ���H��I�����Ă�������.(L)free (R)Read
REM #7-%d���H��I�����Ă�������.(L)free (R)Read
REM #8 ���H��I�����Ă�������.(L)free (R)Read
REM #9-%d���H��I�����Ă�������.(L)free (R)Read
REM #10 ���H��I�����Ă�������.(L)free (R)Read
REM #11-%d���H��I�����Ă�������.(L)free (R)Read
REM #12 ���H��I�����Ă�������.(L)free (R)Read
REM #99#
REM #c �Œ�ڕW�ʐ� ���w��:100�u/_/target_min_area:
REM #c �ő�ڕW�ʐ� ���w��:120�u/_/target_max_area:
REM #hr
REM #e

@REM ���H�A���w��
REM #:3
REM #c ���H�� ���w��:4m/_/road_width:
REM #3-%d �����쐬����ӂ�I�����Ă��������D(L)free (R)Read
REM #4 �����쐬����ӂ�I�����Ă��������D(L)free (R)Read
REM #5-%d�X���I�����Ă�������.(L)free (R)Read
REM #99#
REM #e

@REM ���H�i�V�w��
REM #:2
@REM REM #c �Ԍ����� ���w��:6.8m/_/road_width:
REM #3-%d�X���I�����Ă�������.(L)free (R)Read
REM #99#
REM #e

@REM �v�f����
:1
copy jwc_temp.txt data\jwc_temp1.txt
echo "test"
python data/parameter_in.py data/jwc_temp1.txt %2 %3
@REM pause
goto EXE-%1

@REM ���H�A���w��_����
:3
copy jwc_temp.txt data\jwc_temp2.txt
python data/road_make.py data/jwc_temp2.txt %2
goto END

@REM ���H�i�V�w��_����
:2
copy jwc_temp.txt data\jwc_temp2.txt
python data/un_road_make.py data/jwc_temp2.txt %2
@REM pause
goto END

:END
python binary_split_main.py > jwc_temp.txt
@REM pause