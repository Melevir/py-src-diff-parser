# py-src-diff-parser

*Дисклеймер*: разработка этой библиотеки ещё даже не началась,
поэтому не используйте её. А если вы хотите поучаствовать
в разработке, то вы умный, щедрый и дальновидный программист.


Библиотека для анализа дифов исходного кода на Python 3.

На входе diff-файл, на выходе – список python-related сущностей, которые в
этом дифе были добавлены/удалены/изменены.


## Пример использования


    > python py_diff_analyse.py path/to/diff_file
    Added:
    module.submodule.ClassName#methodname
    
    Edited:
    module.submodule.ClassName#another_methodname

    Deleted:
    module.submodule.OldClass


## Установка

    > git clone git@github.com:Melevir/py-src-diff-parser.git
    > cd py-src-diff-parser
    > pip install -r requirements.txt

