@REM �v�f����
REM ���ɉ����ĕ������܂��D
REM #jww
REM #cd
goto %1
REM #hm�y�v�f���́z |�v�f����|���H�쐬����|���H�쐬�Ȃ�|
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
REM #c �Ԍ� ���w��:7.6m/_/b
REM #c ��n�ʐ� ���w��:100�u/_/c
REM #hr
REM #e

@REM ���H�A���w��
REM #:2
REM #c ���H�� ���w��:4m/_/a
REM #3-%d �����쐬����ӂ�I�����Ă��������D(L)free (R)Read
REM #4 �����쐬����ӂ�I�����Ă��������D(L)free (R)Read
REM #5-%d�X���I�����Ă�������.(L)free (R)Read
REM #99#
REM #e

@REM ���H�i�V�w��
REM #:3
REM #c �Ԍ����� ���w��:6.8m/_/a
REM #3-%d�X���I�����Ă�������.(L)free (R)Read
REM #99#
REM #e

@REM �v�f����
:1
copy jwc_temp.txt jwc_temp1.txt
echo "test"
python �O���ό`/parameter_in.py jwc_temp1.txt %2 %3
goto EXE-%1

@REM ���H�A���w��_����
:2
copy jwc_temp.txt jwc_temp2.txt
python �O���ό`/road_make.py jwc_temp2.txt %2
goto END

@REM ���H�i�V�w��_����
:3
copy jwc_temp.txt jwc_temp2.txt
python �O���ό`/un_road_make.py jwc_temp2.txt %2
goto END

:END
python �O���ό`/split.py > jwc_temp.txt
@REM pause