import winModel
import tensorflow as tf
import sys, getopt, csv, random
import team_stats
import matplotlib.pyplot as plt
import turtle

# Get arguments for input model or output
argv = sys.argv[1:]
inputmodel = None
try:
    opts, args = getopt.getopt(argv,"hi:",["ifile="])
except getopt.GetoptError:
    print('play.py -i <inputmodel>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('play.py -i <inputmodel>')
        sys.exit()
    elif opt in ("-i", "--ifile"):
        inputmodel = ".\\" + arg + ".ckpt"

# Start session
sess = tf.InteractiveSession()
sess.run(tf.global_variables_initializer())

# Load Model
if inputmodel is not None:
    saver = tf.train.Saver()
    saver.restore(sess, inputmodel) # Restore if model exists

teams = {}
# First run through full season to get current data
for i in range(1,5410):
    if i == 3286: # Turns out this game got postponed due to a leaky roof and now nobody has the data except for the final score
        continue
    with open('C:\\Users\\Douglas\\Documents\\Visual Studio 2012\\Projects\\NCAABasketball\\NCAABasketball\\2015-2016\game' + str(i) + '.txt', 'r') as csvfile:
        content = csv.reader(csvfile)
        gameStat = list(content)
        team1 = gameStat[0]
        team2 = gameStat[1]
        if team1[0] in teams and team2[0] in teams:
            # Process Game
            teams[team1[0]].updateStats(team1)
            teams[team2[0]].updateStats(team2)
            if team1[22] <= team2[22]:
                teams[team1[0]].lose()
                teams[team2[0]].win()
            else:
                teams[team1[0]].win()
                teams[team2[0]].lose()
        else:
            # First add team1 to dictionary
            if team1[0] in teams:
                teams[team1[0]].updateStats(team1)
            else:
                teams[team1[0]] = team_stats.team_stats(team1)
            # Now add team2 to dictionary
            if team2[0] in teams:
                teams[team2[0]].updateStats(team2)
            else:
                teams[team2[0]] = team_stats.team_stats(team2)

            if team1[22] <= team2[22]:
                teams[team1[0]].lose()
                teams[team2[0]].win()
            else:
                teams[team1[0]].win()
                teams[team2[0]].lose()

# ----------BRACKET GAME CLASS----------
class bracket_game:
    def __init__(self, x, y, team1=None, team2=None, backBracket1=None, backBracket2=None):
        self.t1 = team1
        self.t2 = team2
        self.bb1 = backBracket1
        self.bb2 = backBracket2
        self.x = x
        self.y = y

    def predict(self, teams):
        self.getPredictions(teams)
        if (self.t1 is None or self.t2 is None):
            print('Missing one or more teams: ', self.t1, self.t2)
            return
        # Get stats of both teams
        team1stats = teams[self.t1].getStatVect()
        team2stats = teams[self.t2].getStatVect()
        diff1 = []
        diff2 = []
        for j in range(len(team1stats)):
            diff1 += [team1stats[j] - team2stats[j]]
            diff2 += [team2stats[j] - team1stats[j]]
            
        # Predict score for first team
        x_data = [team1stats + team2stats + diff1]
        team1ScorePrediction = winModel.y.eval(feed_dict={winModel.x: x_data, winModel.keep_prob: 1.0})[0] # Get output vector from model
        # Predict score for second team
        x_data = [team2stats + team1stats + diff2]
        team2ScorePrediction = winModel.y.eval(feed_dict={winModel.x: x_data, winModel.keep_prob: 1.0})[0] # Get output vector from model
        
        t1WinPct = team1ScorePrediction[0] / (abs(team1ScorePrediction[0]) + abs(team2ScorePrediction[0]))
        t2WinPct = team2ScorePrediction[0] / (abs(team1ScorePrediction[0]) + abs(team2ScorePrediction[0]))
        if t1WinPct <= 0 and t1WinPct == min(t1WinPct, t2WinPct):
            t1WinPct = 0.0
            t2WinPct = 1.0
        if t2WinPct <= 0:
            t2WinPct = 0.0
            t1WinPct = 1.0    
        
        print(self.t1, t1WinPct, self.t2, t2WinPct)# Probably want to display games differently later! Could initialize brackets with coordinate locations for plotting.
        draw_game(self.x, self.y, self.t1, t1WinPct, self.t2, t2WinPct)

        # Return tuple of team1score, team2score, and winner
        if team1ScorePrediction[0] >= team2ScorePrediction[0]:
            return (team1ScorePrediction[0], team2ScorePrediction[0], self.t1) 
        else:
            return (team1ScorePrediction[0], team2ScorePrediction[0], self.t2)
        
    def getPredictions(self, teams):
        if self.t1 is None:
            self.t1 = self.bb1.predict(teams)[2]
        if self.t2 is None:
            self.t2 = self.bb2.predict(teams)[2]

# Set some initial things up
turtle.setup (width=1900, height=1000, startx=0, starty=0)
turtle.speed(0)
        
def draw_game(xin, yin, t1n, t1s, t2n, t2s):
    turtle.penup()
    turtle.setpos(xin,yin)
    turtle.write(t1n + " " + str(t1s), font=("Arial", 10, "normal"))
    turtle.setpos(xin,yin-2) # Negative y is down unlike normal
    turtle.pd()
    turtle.forward(200) # Turtle starts out moving right
    turtle.hideturtle()

    yin = yin - 22
    turtle.penup()
    turtle.setpos(xin,yin)
    turtle.write(t2n + " " + str(t2s), font=("Arial", 10, "normal"))
    turtle.setpos(x,y-4) # Negative y is down unlike normal
    turtle.pd()
    turtle.forward(200) # Turtle starts out moving right
    turtle.hideturtle()
    yin = yin - 32
    
    # Every game should transition -54 down
    

# Initialize all brackets! SWEM
'''
x = -600
y = 480
PIS = bracket_game(x, y, team1='Kansas State', team2='Wake Forest')
x += 300
PIE1 = bracket_game(x, y, team1="Mount St. Mary's", team2='New Orleans')
x += 300
PIM = bracket_game(x, y, team1="North Carolina Central", team2='UC-Davis')
x += 300
PIE2 = bracket_game(x, y, team1='Providence', team2='Southern California')
'''

x = -940
y = 400
FIRSTE1 = bracket_game(x, y, team1='Villanova', team2="Mount St. Mary's")
y -= 54
FIRSTE2 = bracket_game(x, y, team1='Wisconsin', team2='Virginia Tech')
y -= 54
FIRSTE3 = bracket_game(x, y, team1='Virginia', team2='North Carolina-Wilmington')
y -= 54
FIRSTE4 = bracket_game(x, y, team1='Florida', team2='East Tennessee State')
y -= 54
FIRSTE5 = bracket_game(x, y, team1='Southern Mississippi', team2='Southern California')
y -= 54
FIRSTE6 = bracket_game(x, y, team1='Baylor', team2='New Mexico State')
y -= 54
FIRSTE7 = bracket_game(x, y, team1='South Carolina', team2='Marquette')
y -= 54
FIRSTE8 = bracket_game(x, y, team1='Duke', team2='Troy')

y -= 74
FIRSTW1 = bracket_game(x, y, team1='Gonzaga', team2='South Dakota State')
y -= 54
FIRSTW2 = bracket_game(x, y, team1='Northwestern', team2='Vanderbilt')
y -= 54
FIRSTW3 = bracket_game(x, y, team1='Notre Dame', team2='Princeton')
y -= 54
FIRSTW4 = bracket_game(x, y, team1='West Virginia', team2='Bucknell')
y -= 54
FIRSTW5 = bracket_game(x, y, team1='Maryland', team2='Xavier')
y -= 54
FIRSTW6 = bracket_game(x, y, team1='Florida State', team2='Florida Gulf Coast')
y -= 54
FIRSTW7 = bracket_game(x, y, team1="Saint Mary's (CA)", team2='Virginia Commonwealth')
y -= 54
FIRSTW8 = bracket_game(x, y, team1='Arizona', team2='North Dakota')

y = 400
x = 700
FIRSTM1 = bracket_game(x, y, team1='Kansas', team2='UC-Davis')
y -= 54
FIRSTM2 = bracket_game(x, y, team1='Miami (FL)', team2='Michigan State')
y -= 54
FIRSTM3 = bracket_game(x, y, team1='Iowa State', team2='Nevada')
y -= 54
FIRSTM4 = bracket_game(x, y, team1='Purdue', team2='Vermont')
y -= 54
FIRSTM5 = bracket_game(x, y, team1='Creighton', team2='Rhode Island')
y -= 54
FIRSTM6 = bracket_game(x, y, team1='Oregon', team2='Iona')
y -= 54
FIRSTM7 = bracket_game(x, y, team1='Michigan', team2='Oklahoma State')
y -= 54
FIRSTM8 = bracket_game(x, y, team1='Louisville', team2='Jacksonville State')

y -= 74
FIRSTS1 = bracket_game(x, y, team1='North Carolina', team2='Texas Southern')
y -= 54
FIRSTS2 = bracket_game(x, y, team1='Arkansas', team2='Seton Hall')
y -= 54
FIRSTS3 = bracket_game(x, y, team1='Minnesota', team2='Middle Tennessee')
y -= 54
FIRSTS4 = bracket_game(x, y, team1='Butler', team2='Winthrop')
y -= 54
FIRSTS5 = bracket_game(x, y, team1="Cincinnati", team2='Kansas State')
y -= 54
FIRSTS6 = bracket_game(x, y, team1='UCLA', team2='Kent State')
y -= 54
FIRSTS7 = bracket_game(x, y, team1='Dayton', team2='Wichita State')
y -= 54
FIRSTS8 = bracket_game(x, y, team1='Kentucky', team2='Northern Kentucky')

x = -720
y = 300
SECONDE1 = bracket_game(x, y, backBracket1=FIRSTE1, backBracket2=FIRSTE2) # 32 Teams in second round
y -= 54
SECONDE2 = bracket_game(x, y, backBracket1=FIRSTE3, backBracket2=FIRSTE4)
y -= 54
SECONDE3 = bracket_game(x, y, backBracket1=FIRSTE5, backBracket2=FIRSTE6)
y -= 54
SECONDE4 = bracket_game(x, y, backBracket1=FIRSTE7, backBracket2=FIRSTE8)

y = -160
SECONDW1 = bracket_game(x, y, backBracket1=FIRSTW1, backBracket2=FIRSTW2)
y -= 54
SECONDW2 = bracket_game(x, y, backBracket1=FIRSTW3, backBracket2=FIRSTW4)
y -= 54
SECONDW3 = bracket_game(x, y, backBracket1=FIRSTW5, backBracket2=FIRSTW6)
y -= 54
SECONDW4 = bracket_game(x, y, backBracket1=FIRSTW7, backBracket2=FIRSTW8)

x = 480
y = 300
SECONDM1 = bracket_game(x, y, backBracket1=FIRSTM1, backBracket2=FIRSTM2)
y -= 54
SECONDM2 = bracket_game(x, y, backBracket1=FIRSTM3, backBracket2=FIRSTM4)
y -= 54
SECONDM3 = bracket_game(x, y, backBracket1=FIRSTM5, backBracket2=FIRSTM6)
y -= 54
SECONDM4 = bracket_game(x, y, backBracket1=FIRSTM7, backBracket2=FIRSTM8)

y = -160
SECONDS1 = bracket_game(x, y, backBracket1=FIRSTS1, backBracket2=FIRSTS2)
y -= 54
SECONDS2 = bracket_game(x, y, backBracket1=FIRSTS3, backBracket2=FIRSTS4)
y -= 54
SECONDS3 = bracket_game(x, y, backBracket1=FIRSTS5, backBracket2=FIRSTS6)
y -= 54
SECONDS4 = bracket_game(x, y, backBracket1=FIRSTS7, backBracket2=FIRSTS8)

x = -500
y = 240
THIRDE1 = bracket_game(x, y, backBracket1=SECONDE1, backBracket2=SECONDE2) # Sweet Sixteen
y -= 54
THIRDE2 = bracket_game(x, y, backBracket1=SECONDE3, backBracket2=SECONDE4)

y = -220
THIRDW1 = bracket_game(x, y, backBracket1=SECONDW1, backBracket2=SECONDW2)
y -= 54
THIRDW2 = bracket_game(x, y, backBracket1=SECONDW3, backBracket2=SECONDW4)

x = 260
y = 240
THIRDM1 = bracket_game(x, y, backBracket1=SECONDM1, backBracket2=SECONDM2)
y -= 54
THIRDM2 = bracket_game(x, y, backBracket1=SECONDM3, backBracket2=SECONDM4)

y = -220
THIRDS1 = bracket_game(x, y, backBracket1=SECONDS1, backBracket2=SECONDS2)
y -= 54
THIRDS2 = bracket_game(x, y, backBracket1=SECONDS3, backBracket2=SECONDS4)

x = -280
y = 220
FOURTHE1 = bracket_game(x, y, backBracket1=THIRDE1, backBracket2=THIRDE2) # Elite Eight
x = -280
y = -240
FOURTHW1 = bracket_game(x, y, backBracket1=THIRDW1, backBracket2=THIRDW2)
x = 40
y = 220
FOURTHM1 = bracket_game(x, y, backBracket1=THIRDM1, backBracket2=THIRDM2)
x = 40
y = -240
FOURTHS1 = bracket_game(x, y, backBracket1=THIRDS1, backBracket2=THIRDS2)

x = -400
y = 0
EASTWEST = bracket_game(x, y, backBracket1=FOURTHE1, backBracket2=FOURTHW1) # Final Four
x = 160
SOUTHMIDWEST = bracket_game(x, y, backBracket1=FOURTHS1, backBracket2=FOURTHM1)
x = -120
FINAL = bracket_game(x, y, backBracket1=EASTWEST, backBracket2=SOUTHMIDWEST) # CHAMIONSHIP!!!!!!!

# RUN THE BRACKET GENERATOR!
FINAL.predict(teams)
turtle.done()