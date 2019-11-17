import traceback
import sys

class MyExc(Exception):
	def __init__(self, line_num, exc_message):
		self.line_num = line_num
		self.exc_message = exc_message

		
script = '''
#print(44)


def closure(a):
	def my_f(a, b):
		#print(a)
		#print('*************')
		c=str(1/0)
		#print('a' +c)
		#print(b)
		return a*2

	try:
		return my_f(a, 5)
	except Exception as e:
		#print([i for i in e.args])
		#print('-------------------------------')
		#print(traceback_print_exc())
		#print('--------------------------------------')
		cl, exc, tb = sys_exc_info()
		line_number = traceback_extract_tb(tb)[-1][1] -1
		raise MyExc(line_num=line_number, exc_message=e.args[0])

'''

def do(a):
	safe_dict_1 = {"__builtins__" : None, 'print':print, 'traceback_print_exc':traceback.print_exc, 'Exception': Exception, 'traceback_extract_tb':traceback.extract_tb, 'sys_exc_info':sys.exc_info}
	safe_dict = {"__builtins__" : None, 'print':print, 'Exception': Exception, 'traceback_extract_tb':traceback.extract_tb, 'sys_exc_info':sys.exc_info, 'MyExc' : MyExc}
	local = {}
	comp_code = compile(script, '<string>', 'exec')
	exec(comp_code, safe_dict, local)

	
	try:
		#print('first line', comp_code.co_firstlineno)
		#print("\n".join([str(i)+script.split('\n')[i] for i in range(len(script.split('\n')))]))
		result = local['closure'](a)-1
		#use result
		
		#print(script.split('\n')[line].strip())
		#print(get_n_line(script, line).strip())
	except MyExc as e:
		line_n = e.line_num
		msg = e.exc_message
		line = get_n_line(script, line_n).strip()
		print(f'Found error: {msg} \nwhile executing the following line: \n{line}')
	except Exception as e:
		raise
		
def get_n_line(s, n):
	c = 0
	start = -1
	for i in range(len(s)):
		if s[i] == '\n':
			c +=1
			if c == n: 
				start = i
			if c == n+1:
				return s[start:i]