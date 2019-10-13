'''
allowed_functions: can put both built-in and from modules, though make sure to also add the module to required_modules. For both of them you need to add them to a list.
'''

ch1_text = '''
Learn how to code summation in Python. 
You have to
 write a function 
 called <i>my_sum</i> which
 takes two numeric inputs 
 and returns 
 their sum. <br>
Example:
<pre>
In [1]: my_sum(1,2)
Out[1]: 3
</pre>
Possible solution:
<pre>
def my_sum(a,b):
    return a+b
</pre>
'''

my_challenges = [{'id': 1, 'title': 'The + Operation', 
                 'text': ch1_text, 
                 'func_name': 'my_sum', 'max_score': 5, 'tips': ['No tips for this exercise, it is straightforward'], 
                 'allowed_functions': ['math.cos', 'math.sin'], 'required_modules': ['math']},
                 {'id': 2, 'title': 'Reverse Me', 
                  'text': 'Write a function called <i>reverse</i> that takes as input a string and returns another string. In particular, the string returned needs to be the reverse of the original. \nFor example, the word <i>python</i> would become <i>nohtyp</i>. The output needs to be in lowercase letters with no additional whitespaces.', 
                  'func_name': 'reverse', 'max_score': 8, 'tips': ['What if the initial string has an uppercase letter?', 'Note that the string itself may include whitespaces, in that case you have to leave them!'],
                  'allowed_functions': [], 'required_modules': []},
                 {'id': 3, 'title': 'title_3', 'text': 'text_3', 'func_name': 'my_sum', 'max_score': 1, 'tips': [], 'allowed_functions': [], 'required_modules': []},
                 {'id': 4, 'title': 'title_4', 'text': 'text_4', 'func_name': 'my_sum', 'max_score': 1, 'tips': ['tip*4_1', 'tip*4_2', 'tip*4_3', 'tip*4_4'],
                  'allowed_functions': [], 'required_modules': []}
                 ]
