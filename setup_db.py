from app import db
from app.models import Groups, Challenges, ChallengeGroup, Users
import logging

#check correct challenges setup
from source import challenges

def truncate(x, digits):
    return int(10 ** digits * x) / 10 ** digits


#check intro section

intro = challenges.my_challenges[0]
if len(intro) == 0:
    raise Exception('Intro section is missing. If not wanted, set the visible flag to false')
for check in ('id', 'title', 'text', 'allowed_functions', 'required_modules', 'visible'):
    if check not in intro:
        raise Exception(f'The {check} attribute is missing from the intro')
if not isinstance(intro['id'], int):
    raise Exception('The intro id must be an integer')
if intro['id'] != 0:
    raise Exception('The intro id must be equal to 0')
if not isinstance(intro['allowed_functions'], list):
    raise Exception('The intro allowed_functions must be a list of strings. It is not a list')
if not isinstance(intro['required_modules'], list):
    raise Exception('The intro required_modules must be a list of strings. It is not a list')
if not isinstance(intro['title'], str):
    raise Exception('The intro title must be a string')
if not isinstance(intro['text'], str):
    raise Exception('The intro text must be a string')
for item in intro['allowed_functions']:
    if not isinstance(item, str):
        raise Exception('Intro allowed_functions must be a list of string. It does not contain only strings')
for item in intro['required_modules']:
    if not isinstance(item, str):
        raise Exception('Intro required_modules must be a list of string. It does not contain only strings')


#check challenges section

checks = {'id': 'The challenge id is missing, in /source/challenges.py, challenge %d',
 'title': '','text': '','tips': '','allowed_functions': '','required_modules': '', 'func_name': ''}
default_error = 'The challenge %s is missing. In /source/challenges.py, challenge %d'
error_location = '. In /source/challenges.py, challenge %d'

c = challenges.my_challenges[1:]

for i in range(len(c)):
    for check in checks:
        if check not in c[i]:
            if len(checks[check]) != 0:
                error = checks[check] % (i+1)
            else:
                error = default_error % (check, i+1)
            raise Exception(error)

    if not isinstance(c[i]['id'], int):
        raise Exception('Challenge id must be an integer. Error at %s' % str(c[i]['id']) + error_location % (i+1))
    if c[i]['id'] == 0:
        raise Exception('Challenge id must be different from 0, which is reserved for the intro. Error at %s' % str(c[i]['id']) + error_location % (i+1))
    if not isinstance(c[i]['tips'], list):
        raise Exception('Challenge tips must be a list of strings. It is not a list. Error at %s' % str(c[i]['tips']) + error_location % (i+1))
    if not isinstance(c[i]['allowed_functions'], list):
        raise Exception('Challenge allowed_functions must be a list of strings. It is not a list. Error at %s' % str(c[i]['allowed_functions']) + error_location % (i+1))
    if not isinstance(c[i]['required_modules'], list):
        raise Exception('Challenge required_modules must be a list of strings. It is not a list. Error at %s' % str(c[i]['required_modules']) + error_location % (i+1))
    if not isinstance(c[i]['title'], str):
        raise Exception('Challenge title must be a string. Error at %s' % str(c[i]['title']) + error_location % (i+1))
    if not isinstance(c[i]['text'], str):
        raise Exception('Challenge text must be a string. Error at %s' % str(c[i]['text']) + error_location % (i+1))
    if not isinstance(c[i]['func_name'], str):
        raise Exception('Challenge func_name must be a string. Error at %s' % str(c[i]['func_name']) + error_location % (i+1))
    if 'weight' not in c[i]:
        c[i]['weight'] = 1
    if not isinstance(c[i]['weight'], (float, int)):
        raise Exception('Challenge weight must be a number. Error at %s' % str(c[i]['weight']) + error_location % (i + 1))
    c[i]['weight'] = truncate(c[i]['weight'], 4)
    if 'is_simulation' not in c[i]:
        c[i]['is_simulation'] = False
    if not isinstance(c[i]['is_simulation'], bool):
        raise Exception('Challenge is_simulation must be a boolean. Error at %s' % str(c[i]['func_name']) + error_location % (i + 1))

    for tip in c[i]['tips']:
        if not isinstance(tip, str):
            raise Exception('Challenge tips must be a list of string. It does not contain only strings. Error at %s' % str(tip) + error_location % (i+1))
    for item in c[i]['allowed_functions']:
        if not isinstance(item, str):
            raise Exception('Challenge allowed_functions must be a list of string. It does not contain only strings. Error at %s' % str(item) + error_location % (i+1))
    for item in c[i]['required_modules']:
        if not isinstance(item, str):
            raise Exception('Challenge required_modules must be a list of string. It does not contain only strings. Error at %s' % str(item) + error_location % (i+1))

    if i != 0:
        if c[i]['id'] == c[i-1]['id']:
            raise Exception('Challenge ids must be unique' + error_location % (i+1))

#check correct solutions setup
from source import solution

s = solution.my_solutions
error_location = '. In /source/solution.py, solution %d'

if not len(s) == len(c):
    raise Exception('Mismatch between the number of challenges in /source/challenges.py and the number of solutions in /source/solution.py')

for i in range(len(c)):
    c_id = c[i]['id']
    if c_id not in s:
        raise Exception(f'There are no corresponding solutions for the challenge with id {c_id}' + error_location % (c_id))

    cases = s[c_id]
    # compute max score
    c[i]['max_score'] = truncate(len(cases) * c[i]['weight'], 2)


    for i in range(len(cases)):
        if not len(cases[i]) == 2:
            raise Exception('Each test case must be a tuple containing two elements: an input and an output. Error at %s' % str(cases[i]) + error_location % (c_id))
        if not isinstance(cases[i][0], tuple):
            # raise Exception('Each test case input must be contained within a tuple. The tuple can contain multiple inputs. Error at %s' % cases[i][0] + error_location % (c_id))
            cases[i][0] = (cases[i][0],)
        if i != 0:
            if len(cases[i][0]) != len(cases[i-1][0]):
                raise Exception('For a given challenge, each test case must have the same input size. Error at %s' % str(cases[i][0]) + error_location % (c_id))
            if type(cases[i][1]) != type(cases[i-1][1]):
                raise Exception('For a given challenge, each test case must have the same output type. Error at %s' % str(cases[i][1]) + error_location % (c_id))

# check imports and allowed functions work
error_location = '. In /source/challenges.py, challenge %d'


def check_funcs(c, i):
    modules = c['required_modules']
    if len(modules) != 0:
        imports = 'import ' + "\nimport ".join(modules)
        exec(imports)  # here safe to use because this is platform manager generated content
    for f in c['allowed_functions']:
        try:
            eval(f)
        except:
            print("Make sure that the function includes a 'module.function' declaration. Error at %s" % str(f) + error_location % (c_id))
            raise

for i in range(len(c)):
    check_funcs(c[i], i)

check_funcs(intro, 0)

#check if # challenges on Db match # challenges on local version, if not log a warning
#rationale: can't delete them because of (possible) foreign key constraints, yet
#if have more challenges on server will display a cached copy of an old one

if Challenges.query.count() > len(c)+1:
    logging.warning('Found more challenges on Db than on current version, potentially unwanted challenges will be displayed!')

#add challenges and solutions to db

if len(intro['allowed_functions']) > 0:
    logging.warning('Adding functions defined in the intro section to all challenges.')

for i in range(len(c)):
    #pre-process required_modules
    modules = c[i]['required_modules']
    modules.extend(intro['required_modules'])
    c[i]['allowed_functions'].extend(intro['allowed_functions'])
    imports = ''
    if len(modules) != 0:
        imports = 'import ' + "\nimport ".join(modules)

    record = Challenges.query.filter_by(challenge_id=int(c[i]['id'])).first()
    if record is None:
        new_chall = Challenges(challenge_id=c[i]['id'], specification=str(c[i]), allowed_functions=str(c[i]['allowed_functions']),
                               required_modules=imports, solutions=str(s[c[i]['id']]), func_name=c[i]['func_name'].strip(),
                               max_score = c[i]['max_score'], weight = c[i]['weight'], title=c[i]['title'],
                               is_simulation = c[i]['is_simulation'])
        db.session.add(new_chall)
    else:
        record.specification = str(c[i])
        record.allowed_functions = str(c[i]['allowed_functions'])
        record.required_modules = imports
        record.solutions = str(s[c[i]['id']])
        record.func_name = c[i]['func_name'].strip()
        record.max_score = c[i]['max_score']
        record.weight = c[i]['weight']
        record.is_simulation = c[i]['is_simulation']
        record.title = c[i]['title']

# handling intro

record = Challenges.query.filter_by(challenge_id=-1).first()
if record is None:
    new_chall = Challenges(challenge_id=intro['id']-1, specification=str(intro), allowed_functions='',
                           required_modules= '', solutions= '', func_name= '', weight= 0, is_simulation= False,
                           max_score= 0, title='')
    db.session.add(new_chall)
else:
    record.specification = str(intro)

db.session.commit()
