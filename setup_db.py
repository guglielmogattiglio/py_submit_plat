from app import db
from app.models import Groups, Challenges, ChallengeGroup, Users

#empty db
ChallengeGroup.query.delete()
Users.query.delete()
Groups.query.delete()
Challenges.query.delete()
db.session.commit()

#check correct challenges setup
from source import challenges

checks = {'id': 'The challenge id is missing, in /source/challenges.py, challenge %d',
 'title': '','text': '','max_score': '','tips': '','allowed_functions': '','required_modules': '', 'func_name': ''}
default_error = 'The challenge %s is missing. In /source/challenges.py, challenge %d'
error_location = '. In /source/challenges.py, challenge %d'

c = challenges.my_challenges

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
    if not isinstance(c[i]['max_score'], int):
        raise Exception('Challenge max_score must be an integer. Error at %s' % str(c[i]['max_score']) + error_location % (i+1))
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
    if len(cases) != c[i]['max_score']:
        raise Exception('Number of test cases different from corresponding challenge max_score' + error_location % (c_id))
        
    
    for i in range(len(cases)):
        if not len(cases[i]) == 2:
            raise Exception('Each test case must be a tuple containing two elements: an input and an output. Error at %s' % str(cases[i]) + error_location % (c_id))
        if not isinstance(cases[i][0], tuple):
            #raise Exception('Each test case input must be contained within a tuple. The tuple can contain multiple inputs. Error at %s' % cases[i][0] + error_location % (c_id))
            cases[i][0] = (cases[i][0],)
        if i != 0:
            if len(cases[i][0]) != len(cases[i-1][0]):
                raise Exception('For a given challenge, each test case must have the same input size. Error at %s' % str(cases[i][0]) + error_location % (c_id))
            if type(cases[i][1]) != type(cases[i-1][1]):
                raise Exception('For a given challenge, each test case must have the same output type. Error at %s' % str(cases[i][1]) + error_location % (c_id))

#check imports and allowed functions work
error_location = '. In /source/challenges.py, challenge %d'

def check_funcs(c, i):
    modules = c['required_modules']
    if len(modules) != 0:
        imports = 'import ' + "\nimport ".join(modules)
        exec(imports) #here safe to use because this is platform manager generated content
    for f in c['allowed_functions']:
        try:
            eval(f)
        except:
            print("Make sure that the function includes a 'module.function' declaration. Error at %s" % str(f) + error_location % (c_id))
            raise
    
for i in range(len(c)):
    check_funcs(c[i], i)


#add challenges and solutions to db
for i in range(len(c)):
    #pre-process required_modules
    modules = c[i]['required_modules']
    if len(modules) != 0:
        imports = 'import ' + "\nimport ".join(modules)
    
    new_chall = Challenges(challenge_id=c[i]['id'], specification=str(c[i]), allowed_functions=str(c[i]['allowed_functions']), 
                           required_modules=imports, solutions=str(s[c[i]['id']]), func_name=c[i]['func_name'].strip())
    db.session.add(new_chall)
db.session.commit()
