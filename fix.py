def camel_case_split(str):
    words = [[str[0]]]

    for c in str[1:]:
        if words[-1][-1].islower() and c.isupper():
            words.append(list(c))
        else:
            words[-1].append(c)

    return [''.join(word) for word in words]


def is_verb_es(word):
    type_verb = camel_case_split(word)[0][-2:]
    return type_verb == 'ar' or type_verb == 'er' or type_verb == 'ir'


def quant_params(line):
    params = line[line.find("(") + 1:line.find(")")]
    return len(list(filter(lambda n: n, params.split(','))))


def quant_holes(line):
    return line.count('_')

def is_proposite(word):
    lower_word = word.lower()
    return lower_word == 'propósito' or lower_word == 'proposito' or lower_word == 'propósito:' or lower_word == 'proposito:'

def has_propouse(words):
    for w in words:
        if is_proposite(w):
            return True
            break
    return False

def is_precond(word):
    l_w = word.lower()
    return l_w == 'precondiciones' or l_w == 'precondicion' or l_w == 'precondición' or l_w == 'precondiciones:' or l_w == 'precondicion:' or l_w == 'precondición:'

def has_precondition(words):
    for w in words:
        if is_precond(w):
            return True
    return False


def start_correction(text):
    lines = text.splitlines()
    clean_lines =list(map(lambda n: n.replace("\n", ""), lines))
    # clean_lines = list(filter(lambda n : n, clean_lines))
    errors = []

    for idx, line in enumerate(clean_lines):
        errors.append(str(idx)+ ' ' + line)
    errors.append('\n \n')
    for idx, line in enumerate(clean_lines):
        words = line.split()
        if words and words[0] == 'procedure':
            if not words[1][0].isupper():
                errors.append('[error line: {idx}] - El nombre del procedimiento "{words}" debe comienza con Mayuscula'.format(idx=idx, words=words[1]))
            if not is_verb_es(words[1]):
                errors.append('[error line: {idx}] - El nombre del procedimiento "{words}" debe tener como primer palabra un verbo en infinitivo'.format(idx=idx, words=words[1]))
        if words and words[0] == 'function':
            if words[1][0].isupper():
                errors.append('[error line: {idx}] - El nombre de la funcion "{words}" debe comienza con minuscula'.format(idx=idx, words=words[1]))
            if is_verb_es(words[1]):
                errors.append('[error line: {idx}] - El nombre de la funcion "{words}" no debe tener como primer palabra un verbo'.format(idx=idx, words=words[1]))

        if words and words[0] == 'procedure' or words and words[0] == 'function':
            if quant_params(line) != quant_holes(line):
                errors.append('[error line: {idx}] - El numero de "_" en el nombre del procedimiento "{words}" debe ser el mismo al numero de parametros'.format(idx=idx, words=words[1]))
            params_ = line[line.find("(")+1:line.find(")")]
            params = list(filter(lambda n: n, params_.split(',')))
            for x in params:
                if is_verb_es(x):
                    errors.append('[error line: {idx}] - El nombre del parametro "{words}" no debe tener como primer palabra un verbo'.format(idx=idx, words=x))
            if len(words[1].split('(')[0]) < 7:
                errors.append('[error line: {idx}] - Mal nombre de {tipo}, que comunica la palabra "{words}"?'.format(idx=idx,tipo=words[0], words=words[1].split('(')[0]))
            if line.count('(') != 1 or line.count(')') != 1:
                errors.append('[error line: {idx}] - Hay parentesis que no corresponden'.format(idx=idx))

    lines_without_emptys = list(filter(lambda n: n, clean_lines))
    comments = False
    res = []
    for line in lines_without_emptys:

        if len(line.strip()) > 1 and line.strip()[:2] == '//':
            continue
        if len(line.strip()) > 1 and line.strip()[:2] == '/*':
            comments = True
            continue
        if len(line.strip()) > 1 and line.strip()[:2] == '*/':
            comments = False
            continue
        if comments:
            continue
        res.append(line)

    keys_open = 0
    keys_close = 0
    brackets_open = 0
    brackets_close = 0

    for code in res:
        keys_open += code.count('{')
        keys_close += code.count('}')
        brackets_open += code.count('(')
        brackets_close += code.count(')')
    # falta ver si estan todas abeiertas o cerradasdkg
    if keys_open != keys_close:
        errors.append(
            '[error] - Hay {keys_open} llaves que abren, pero {keys_close} llaves que cierran'.format(keys_open=keys_open,
                                                                                                      keys_close=keys_close))
    if brackets_open != brackets_close:
        errors.append(
            '[error] - Hay {brackets_open} parentesis que abren, pero {brackets_close} parentesis que cierran'.format(
                brackets_open=brackets_open, brackets_close=brackets_close))

    keys = 0
    fop = []
    groups = []
    for x in clean_lines:
        words = x.split()
        if fop and (words and words[0] == 'procedure' or words and words[0] == 'function'):
            groups.append(fop)
            fop = [x]
        else:
            fop.append(x)
    groups.append(fop)

    count = 0
    init_pof = 0
    for y in groups:
        is_checkeable = False
        has_prop = False
        has_prec = False
        for w in y:
            words = w.split()
            count +=1
            if not is_checkeable and (words[0] == 'procedure' or words and words[0] == 'function'):
                is_checkeable = True
                init_pof = count
            if is_checkeable and words:
                if has_propouse(words):
                    has_prop = True
                if has_precondition(words):
                    has_prec = True
        if is_checkeable:
            if not has_prop:
                errors.append('[error line: {idx}] - El procedimiento o funcion no tiene propósito o esta mal escrito'.format(idx=init_pof))
            if not has_prec:
                errors.append('[error line: {idx}] - El procedimiento o funcion no tiene precondiciones o esta mal escrito'.format(idx=init_pof))
    return errors