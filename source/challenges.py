'''
allowed_functions: can put both built-in and from modules, though make sure to also add the module to required_modules. For both of them you need to add them to a list.
'''

intro_text = '''
<b>Read the instructions</b>
<br><br>
<b>Read the instructions</b>
<br><br>
<p>
Seriously, <b>read the instructions</b> (go back to the home page, just click on change group). If you don't, you will not understand how things work around here, especially you will have an hard time debugging your code.
</p>
<p>
The following funcions will be allowed throughout the challenge, unless otherwise instructed by the specific exercise: <i>len</i>, <i>range</i>, <i>max</i>, <i>min</i>, <i>abs</i>, <i>round</i>, <i>sum</i>, <i>built-in types constructors</i> (like int, str, etc), and <i>user created functions</i>. No external module is available. Note that calling a function not listed among one of the above will raise a NoneType exception (read instructions), however you can call your own functions.
</p>
'''

ch1_text = '''
<blockquote>
Hello there! Thank you for acquiring your first robot from us, we are sure it is going to be a <i>very</i> particular experience for you. If you are scared of apocalyptic scenarios where the robots rise and subdue humans, you don't have to worry, because our robots are premium products thoroughly tested with our highest standards.
</blockquote>
<br>
<p>
Our robot received some damage to its GPS system, now he continuously gets lost!! Will you be able to help him? 
Our robot can move among the 4 directions:  NORTH, SOUTH, WEST and EAST. When he receives the indications he perfectly executes them, only that once he executed them he doesn’t know the distance from his starting position. 
</p>
<p> You  have  to  create  a  function  named <i>dist</i> that  accepts  as  argument  a  list. The  list  contains 4 integers.  The first integers represents the total number of steps towards north, the second towards south, the third towards west and the fourth towards east.
The function should output the distance from the starting position.
</p>
<p>
Example:
<pre>
dist([1,0,1,0])
</pre>
Should output: 
<pre>
1.4142135623730951
</pre>
'''

ch2_text = '''
<p>
The robot has an amazing text synthesizer only that you find it really boring. How to make it funnier? After a lot of time spent thinking about solutions such as making him speak in reverse order you decide to make it funnier using the La-La-Land logic. <br>
In order to make it possible you have to write a function called <i>py_py_python</i> that takes a string containing only letters [A-Za-z],the four symbols that are common in every day sentences [.,'?] and spaces, and outputs the string in the style of La La Land.
</p>
Example:
<pre>
py_py_python('Land')
</pre>
Should output: 
<pre>
'La La Land'
</pre>
<p>
To be more specific, take the letters up to, and including, the first vowel group, and returns it twice adding a space each time, then returns the whole string. Note that y is a vowel in this challenge. Punctuation and capitalization should be kept.
</p>
<p>
You may assume that all strings contain at least one vowel, and that all strings start with a letter.
</p>

'''
ch3_text = '''
<p>
Our brave brave robot arrived in India.  Here he is mesmerised by the amazing harmony and symmetry of the Rangoli art. He refuses to continues in his adventures if you do not teach him how to create such an amazing art. 
Your task is to write a function named <i>rangoli</i> that creates an alphabet rangoli. This function should take as input an integer and return a string that, if printed, should appear as follows.
</p>
<p>
NB: you will get a score of zero if you only print the string without returning it, as the platform does not capture stdout (for example everything that is printed to the console using <i>print</i>) but only what the function returns. In Python a function without return statement returns <i>None</i>.
</p>
Different sizes of alphabet rangoli are shown below:
<pre>
print(rangoli(3))
----c----
--c-b-c--
c-b-a-b-c
--c-b-c--
----c----

print(rangoli(5))
--------e--------
------e-d-e------
----e-d-c-d-e----
--e-d-c-b-c-d-e--
e-d-c-b-a-b-c-d-e
--e-d-c-b-c-d-e--
----e-d-c-d-e----
------e-d-e------
--------e--------

print(rangoli(10))
------------------j------------------
----------------j-i-j----------------
--------------j-i-h-i-j--------------
------------j-i-h-g-h-i-j------------
----------j-i-h-g-f-g-h-i-j----------
--------j-i-h-g-f-e-f-g-h-i-j--------
------j-i-h-g-f-e-d-e-f-g-h-i-j------
----j-i-h-g-f-e-d-c-d-e-f-g-h-i-j----
--j-i-h-g-f-e-d-c-b-c-d-e-f-g-h-i-j--
j-i-h-g-f-e-d-c-b-a-b-c-d-e-f-g-h-i-j
--j-i-h-g-f-e-d-c-b-c-d-e-f-g-h-i-j--
----j-i-h-g-f-e-d-c-d-e-f-g-h-i-j----
------j-i-h-g-f-e-d-e-f-g-h-i-j------
--------j-i-h-g-f-e-f-g-h-i-j--------
----------j-i-h-g-f-g-h-i-j----------
------------j-i-h-g-h-i-j------------
--------------j-i-h-i-j--------------
----------------j-i-j----------------
------------------j------------------
</pre>
'''



ch4_text = '''
<p>
After his trip to India it is time for the robot to go back to the wonderful ACademy of Marvellous Electronics (ACME).
ACME offers rewards in the form of amazing updates to robots with good attendance and punctuality. If they are absent for three consecutive days or late on more than one occasion then they forfeit their prize.
</p>
<p>
During an n-day period a trinary string is formed for each robot consisting of L's (late), O's (on time), and A's (absent).
</p>
<p>
Although there are eighty-one trinary strings for a 4-day period that can be formed, exactly forty-three strings would lead to a prize:
</p>
<p>
<pre>
OOOO OOOA OOOL OOAO OOAA OOAL OOLO OOLA OAOO OAOA
OAOL OAAO OAAL OALO OALA OLOO OLOA OLAO OLAA AOOO
AOOA AOOL AOAO AOAA AOAL AOLO AOLA AAOO AAOA AAOL
AALO AALA ALOO ALOA ALAO ALAA LOOO LOOA LOAO LOAA
LAOO LAOA LAAO
</pre>
</p>
<p>
How many "prize" strings exist over a 30-day period? Write a function called <i>prizes</i> that computes the desired number (hint: in this exercise you are likely to get "Timed out").
</p>
'''

ch5_text = '''

<p>
ACME courses are tough and with many homeworks, after studies our robot enjoys spending the evening at the local robo-pub. Here between a pint of oil and the other he discovers the intriguing and complicated game of darts.
When he returns home he explains you that in the game of darts a player throws three darts at a target board which is split into twenty equal sized sections numbered one to twenty.



</p>

<p>
  <img src="http://www.darts.org.nz/image/board.jpg">
  </p>
<p>
  </p>
<p>
  </p>
<p>
<p>
The score of a dart is determined by the number of the region that the dart lands in. A dart landing outside the red/green outer ring scores zero. The black and cream regions inside this ring represent single scores. However, the red/green outer ring and middle ring score double and treble scores respectively.
</p>
<p>
At the centre of the board are two concentric circles called the bull region, or bulls-eye. The outer bull is worth 25 points and the inner bull is a double, worth 50 points.
</p>
<p>
There are many variations of rules but in the most popular game the players will begin with a score 301 or 501 and the first player to reduce their running total to zero is a winner. However, it is normal to play a "doubles out" system, which means that the player must land a double (including the double bulls-eye at the centre of the board) on their final dart to win; any other dart that would reduce their running total to one or lower means the score for that set of three darts is "bust".
</p>
<p>
When a player is able to finish on their current score it is called a "checkout" and the highest checkout is 170: T20 T20 D25 (two treble 20s and double bull).
</p>
<p>
There are exactly eleven distinct ways to checkout on a score of 6:

<table style="width:100%">
  <tr>
    <th>First throw</th>
    <th>Second throw</th>
    <th>Third throw</th>
  </tr>
  <tr>
    <td>D3</td>
    <td>0</td>
    <td>0</td>
  </tr>
  <tr>
    <td>D1</td>
    <td>D2</td>
    <td>0</td>
  </tr>
  <tr>
    <td>S2</td>
    <td>D2</td>
    <td>0</td>
  </tr>
  <tr>
    <td>D2</td>
    <td>D1</td>
    <td>0</td>
  </tr>
  <tr>
    <td>S4</td>
    <td>D1</td>
    <td>0</td>
  </tr>
  <tr>
    <td>S1</td>
    <td>S1</td>
    <td>D2</td>
  </tr>
  <tr>
    <td>S1</td>
    <td>T1</td>
    <td>D1</td>
  </tr>
  <tr>
    <td>S1</td>
    <td>S3</td>
    <td>D1</td>
  </tr>
  <tr>
    <td>D1</td>
    <td>D1</td>
    <td>D1</td>
  </tr>
  <tr>
    <td>D1</td>
    <td>S2</td>
    <td>D1</td>
  </tr>
  <tr>
    <td>S2</td>
    <td>S2</td>
    <td>D1</td>
  </tr>
</table>
</p>
<p>
Note that D1 D2 is considered different to D2 D1 as they finish on different doubles. However, the combination S1 T1 D1 is considered the same as T1 S1 D1.
</p>
<p>
In addition we shall not include misses in considering combinations; for example, D3 is the same as 0 D3 and 0 0 D3.
</p>
<p>
Incredibly there are 42336 distinct ways of checking out in total.
Our robot is distressed by the following question: 'How many distinct ways can a player checkout with a score less than 100?' You have to write a function called <i>combinations</i> that takes no inputs, computes the total number of possible player checkouts and returns it as an integer.
  </p>
'''

ch6_text = '''
<p>
If you have ever had a garden, you'd know how painful it is to water all the flowers (literally, carrying all that water up and down the stairs - only the thought makes my back hurt), so one day you buy a Robot Gardener Update for your robot that, supposedly, should make the robot take care of the flowers. You start reading the instruction:
</p>
<blockquote>
"...The Robot Gardener expects all plants to be arranged in a rectangular flowerbed. Within this space, it will water each plant once per day, before sunset. Note that due to the poor design of this robot, when watering one plant there will be spillover effects to all neighbouring plants, so it will be basically watering 9 plants while believing it was just one."
</blockquote>
<p>
Since you want to have the best flowerbed in you town, each spot is either occupied by a flower or a seed. During the night, flowers and seeds respond to the water received throughout the day in a peculiar way: if they have received the right amount of water they will grow, otherwise they will regress if they got too much or too little water. Assume that, instead of dying, the plant will just go back to seed. The behaviour of the plant as a function of units of water is plant specific, for example a specific variety could regress by one if it gets 0-2 water, grow by 1 if it gets 3 water, grow by 2 if it gets 4, remain indifferent if it gets 5 and regress by 2 if it gets more than 6. Note that a plant will never receive more than 9 units of water (why?).
</p>
<p>
Assume you have to go on vacation for <i>k</i> days, given an initial configuration of your garden and a set of rules for your flowers (assume for simplicity you have only one kind of flower in the whole garden), how will the flowerbed look like when you get back, knowing that you had your Robot Gardener watering all of them for you? Which of them will be alive and how tall?
</p>
<p>
Specifically, write a function called <i>water_vacation</i> with takes as input a matrix (the initial flowerbed), represented as a list of lists, containing the height of the flower or 0 if it is a seed; the total number of days <i>k</i>; and a list representing growth rules, where each index <i>i</i> of the list specifies by how much the plant grows/regresses when receiving <i>i</i> units of water. It needs to return the final flowerbed configuration as a list of lists (same format as input matrix).
</p>

Example:
<pre>
flowerbed=[[1,0,1,1],
           [0,0,3,0],
           [1,0,2,0]
          ]
k = 3
rules = [-1,-1,0,1,3,0,0,0,0,0]

print(water_vacation(flowerbed, k, rules))
[[0, 3, 2, 8], [0, 0, 6, 3], [0, 3, 5, 4]]
</pre>

In details, this is what is happening:
<pre>
Turn    flowerbed    water
0       1 0 1 1      1 3 3 3
        0 0 3 0      2 5 4 4
        1 0 2 0      1 3 2 2
      
Turn    flowerbed    water
1       0 1 2 2      1 3 5 4
        0 0 6 3      2 5 7 5
        0 1 2 0      1 3 4 3
        
Turn    flowerbed    water
2       0 2 2 5      1 3 5 4
        0 0 6 3      2 5 8 6
        0 2 5 1      1 3 5 4
        
Turn    flowerbed    
3       0 3 2 8
        0 0 6 3
        0 3 5 4
</pre>
'''

my_challenges = [{'id': 0, 'title':'Intro', 'text': intro_text,
                  'allowed_functions': ['range', 'len', 'max', 'min', 'abs', 'bool', 'dict', 'list', 'str', 'int', 'float', 'set', 'round'],
                  'required_modules': [], 'visible': True},
                 {'id': 1, 'title': 'Robot Position', 'text': ch1_text, 'func_name': 'dist', 'max_score': 5, 'tips':
                    ['Remember that in order that the formula of the euclidean distance is the square root of the squared movement along the x and the squared movement along the y'],
                  'allowed_functions': [],
                  'required_modules': []},
                  {'id': 2, 'title': 'La La Land..? Py Py Python!', 'text': ch2_text, 'func_name': 'py_py_python', 'max_score': 5, 'tips': [],
                  'allowed_functions': [],
                  'required_modules': []},
                 {'id': 3, 'title': 'Rangoli', 'text': ch3_text, 'func_name': 'rangoli', 'max_score': 5, 'tips':
                     ['Start creating only the top right of the piece of art',
                      'Remember that a string multiplied by an integer results in a new string repeated n times',
                      'Look which one is the special character for a new line'],
                  'allowed_functions': [],
                   'required_modules': []},
                 {'id': 4, 'title': 'Good Good Robot', 'text': ch4_text, 'func_name': 'prizes', 'max_score': 1, 'tips': ['A brute force approach will take forever to run, you need to exploit recursion', "Notice that you don't have to compute all possible case explicitly, if a very long sequence starts with LL, then you can cut all the possible combinations that would follow (aka pruning the tree)", 'Even if you computed the minimum possible of this sequences, that will still not be enough, you need to cache some operations (if you analyze intermediate steps you will recognize that some are just repeated'], 'allowed_functions': [], 'required_modules': []},
                 {'id': 5, 'title': 'Darts Championship', 'text': ch5_text, 'func_name': 'combinations', 'max_score': 1, 'tips': ['You may find useful to "write down" all possible dart combination/score...'],
                  'allowed_functions': [], 'required_modules': []},
                 {'id': 6, 'title': 'Robot Gardener', 'text': ch6_text, 'func_name': 'water_vacation', 'max_score': 14,
				 'tips': 
					['Plants will never receive more than 9 units of water because, at most, all the 8 neighbors will water it plus one unit for itself. Check for this with an assert, you can prevent bugs',
					"It's useful to divide the process into two steps: constructing the <i>water</i> matrix out of current <i>flowerbed</i> configuration, and then updating the flowerbed based on the <i>water</i> matrix. Then repeat k times.",
					'To construct the <i>water</i> matrix, one way to approach this can be to do one pass over <i>flowerbed</i> and for each cell update all the relevant cells in <i>water</i>. This can be a bit tricky, think about it and read next tip if you are lost.',
					"To update <i>water</i>, consider as an example <i>flowerbed</i> to be a 5x5 square matrix and consider plant (3, 3). Assume further that <i>flowerbed</i>[3][3] > 0 (it's not a seed), then ideally one would like to do something like <br><br> water[2:5][2:5] += 1 #increasing amount of water for each neighboring plant<br><br>Clearly that's just pseudocode as it doesn't work with lists. Can you implement a similar behaviour?"
					], 
				 'allowed_functions': [],
                   'required_modules': []},
                 ]
