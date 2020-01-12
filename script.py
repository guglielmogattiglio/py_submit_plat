from EvalException import MyExc, get_n_line
import sys
import re
import func_timeout
import traceback
import ast
import math
import logging


def extract_script(json):
    script = json['script']
    c_id = json['challenge_id']
    group_name = json['group']
    return script, c_id, group_name


def make_safe_dict(allowed_functions, required_modules):
    safe_dict = {}
    exec(required_modules)
    for f in ast.literal_eval(allowed_functions):
        f_name = extract_f_name(f)
        safe_dict[f_name] = eval(f)
        safe_dict[f] = eval(f)
    return safe_dict


def extract_f_name(f):
    i = f.find('.')
    while i >= 0:
        f = f[i + 1:]
        i = f.find('.')
    return f


def validate_script(script):
    # first remove import
    script = re.sub(r'from.*?import.*|import.*', '', script)
    # remove comments (validated keywords could be contained inside)
    script = re.sub(r'#.*', '', script)
    #script = re.sub(r"'''.*?'''", '', script, flags=re.S)
    # prevent from exploiting eval
    if '__' in script:
        raise Exception('You are not allowed to use/call reserved names delimited by __')
    return script


def evaluate_script(script, safe_dict, func_name, sol, sleep, timeout, max_score, is_sim):
    no_builtins_dic = {"__builtins__": None, 'Exception': Exception,
                       'traceback_extract_tb': traceback.extract_tb, 'sys_exc_info': sys.exc_info,
                       'MyExc': MyExc, 'KeyError': KeyError}
    safe_dict.update(no_builtins_dic)  # keys already existing will be overwritten
    local = {}
    script = wrap_script(script, func_name)

    try:
        comp_code = compile(script, '<string>', 'exec')
    except SyntaxError as e:
        cl, exc, tb = sys.exc_info()
        line = traceback.format_exception(cl, exc, tb)[-3]
        exc_type = traceback.format_exception(cl, exc, tb)[-1].strip()
        raise Exception(f'{exc_type} raised while executing:\n<p style="white-space: pre;">{line}</p>.') from None
    exec(comp_code, safe_dict, local)

    sol = ast.literal_eval(sol)
    outcome = []
    outcome_short = []  # 1=pass, 0=fail, -1=timed-out
    score = 0
    c = 1

    try:
        for test in sol:
            sleep(0)
            try:
                ret_value = func_timeout.func_timeout(float(timeout), local[func_name], args=test[0])
                if is_sim:
                    if c > 1:
                        continue
                    if ret_value > test[1]:  # make it symmetric
                        ret_value = test[1] - (ret_value - test[1])
                    mid = test[1] / 2
                    if abs(ret_value - test[1]) < 1e-5:
                        outcome.append(f'test {c}: passed')
                        outcome_short.append(1)
                        score += max_score
                    elif ret_value > mid:
                        max_value = test[1] - mid
                        b = 5
                        a = math.log(max_score) - b * math.log(max_value)
                        temp_score = math.exp(a + b * math.log(ret_value-mid))

                        # want to give partial points but want to favor a right solution, if wrong sol can get up to (1-gap)% of max_score
                        high_gap = 0.15
                        low_gap = 0.01
                        if (max_score - temp_score)/max_score < high_gap:
                            temp_score = max_score * (1 - high_gap)
                        # the max is needed because if 1% of max_score is < 0.01, it will be seen as a 0 by the platform and will show
                        # ".. partial points given, your score is 0" when should be >0
                        elif temp_score < max(1e-02, max_score * low_gap):  # give 1% if over half but too close to zero
                            temp_score = max(1e-02, max_score * low_gap)
                        score += temp_score
                        outcome.append(f'test {c}: failed, but partial points were given')
                        outcome_short.append(0)
                    else:
                        outcome.append(f'test {c}: failed')
                        outcome_short.append(0)
                else:
                    if isinstance(test[1], float) or isinstance(ret_value, float):
                        cond = abs(ret_value - test[1]) < 1e-5
                    else:
                        cond = ret_value == test[1]

                    if cond:
                        outcome.append(f'test {c}: passed')
                        outcome_short.append(1)
                        score += 1
                    else:
                        outcome.append(f'test {c}: failed')
                        outcome_short.append(0)
            except func_timeout.exceptions.FunctionTimedOut:
                outcome.append(f'test {c}: timed out')
                outcome_short.append(-1)
            c += 1
            yield score, outcome, outcome_short
    except KeyError:
        raise Exception(
            'KeyError raised during execution: check that your function is called <i>%s</i>.' % func_name) from None
    except TypeError as e:
        raise Exception(str(e)) from None
    except MyExc as e:
        line_n = e.line_num
        msg = e.exc_message
        line = get_n_line(script, line_n).strip()
        raise Exception(f'Found error: {msg} \nwhile executing the following line: \n{line}') from None


# need to wrap original source code into function otherwise other objects are not seen
def wrap_script(script, func_name):
    script = script.split('\n')
    script = "\n    ".join(script)
    script = f'''
def {func_name}(*input):
    {script}
    try:
        {func_name}
    except:
        raise KeyError
    try:
        return {func_name}(*input)
    except Exception as e:
        cl, exc, tb = sys_exc_info()
        line_number = traceback_extract_tb(tb)[-1][1] -1
        raise MyExc(line_num=line_number, exc_message=e.args[0])
    '''
    return script
