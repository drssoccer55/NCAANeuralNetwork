import winModel
import tensorflow as tf
import sys, getopt, csv, random
import team_stats
import matplotlib.pyplot as plt

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
predictableGames = 0
correctPrediction = 0
wrongPrediction = 0
truePositive = 0
falsePositive = 0
trueNegative = 0
falseNegative = 0
tp = []
fp = []
tn = []
fn = []

for i in range(1,5500):
    with open('C:\\Users\\Douglas\\Documents\\Visual Studio 2012\\Projects\\NCAABasketball\\NCAABasketball\\2014-2015\game' + str(i) + '.txt', 'r') as csvfile:
        content = csv.reader(csvfile)
        gameStat = list(content)
        team1 = gameStat[0]
        team2 = gameStat[1]
        if team1[0] in teams and team2[0] in teams:
            # NEED TO DO SOME ACTUAL LISTING HERE
            # Get stats of both teams
            team1stats = teams[team1[0]].getStatVect()
            team2stats = teams[team2[0]].getStatVect()
            diff1 = []
            diff2 = []
            for j in range(len(team1stats)):
                diff1 += [team1stats[j] - team2stats[j]]
                diff2 += [team2stats[j] - team1stats[j]]
            
            # Get win prediction for first team
            x_data = [team1stats + team2stats + diff1]
            team1ActualScore = float(team1[22])
            team1ScorePrediction = winModel.y.eval(feed_dict={winModel.x: x_data, winModel.keep_prob: 1.0})[0] # Get output vector from model
            # Get win prediction for second team
            x_data = [team2stats + team1stats + diff2]
            team2ActualScore = float(team2[22])
            team2ScorePrediction = winModel.y.eval(feed_dict={winModel.x: x_data, winModel.keep_prob: 1.0})[0] # Get output vector from model

            # Analyze!!!
            predictableGames += 1
            if (team1ActualScore >= team2ActualScore) and (team1ScorePrediction > team2ScorePrediction):
                correctPrediction += 1
            elif (team1ActualScore <= team2ActualScore) and (team1ScorePrediction < team2ScorePrediction):
                correctPrediction += 1
            else:
                wrongPrediction += 1
                
            t1WinPct = team1ScorePrediction / (abs(team1ScorePrediction) + abs(team2ScorePrediction))
            t2WinPct = team2ScorePrediction / (abs(team1ScorePrediction) + abs(team2ScorePrediction))
            if t1WinPct <= 0 and t1WinPct == min(t1WinPct, t2WinPct):
                t1WinPct = 0.0
                t2WinPct = 1.0
            if t2WinPct <= 0:
                t2WinPct = 0.0
                t1WinPct = 1.0    
            
            # MORE ANALYSIS HERE
            if (team1ScorePrediction > team2ScorePrediction) and (team1ActualScore >= team2ActualScore):
                truePositive += 1
                tp += [t1WinPct]
                tn += [t2WinPct]
            elif (team1ScorePrediction > team2ScorePrediction) and (team1ActualScore < team2ActualScore):
                falsePositive += 1
                fp += [t1WinPct]
                fn += [t2WinPct]
            elif (team1ScorePrediction < team2ScorePrediction) and (team1ActualScore <= team2ActualScore):
                trueNegative += 1
                tp += [t2WinPct]
                tn += [t1WinPct]
            else:
                falseNegative += 1
                fp += [t2WinPct]
                fn += [t1WinPct]
            
            # Process Game now that analysis is done
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
                
print("Predicatable Games: ", predictableGames)
print("Correct: ", correctPrediction)
print("Wrong: ", wrongPrediction)
print("True Positives: ", truePositive)
print("False Positives: ", falsePositive)
print("True Negatives: ", trueNegative)
print("False Negatives: ", falseNegative)

plt.figure(1)
plt.plot(tp, 'bo', ms=4, label='True Positives')
plt.ylabel('Win %')
plt.xlabel('Sequential Games')
plt.xlim([0,truePositive + trueNegative])
plt.ylim([0,1.2])
plt.title('Predicted Win Percentages of True Positives on the 2014-2015 NCAA Mens Season')
plt.legend()

plt.figure(2)
plt.plot(fp, 'ro', ms=4, label='False Positives')
plt.ylabel('Win %')
plt.xlabel('Sequential Games')
plt.xlim([0,falsePositive + falseNegative])
plt.ylim([0,1.2])
plt.title('Predicted Win Percentages of False Positives on the 2014-2015 NCAA Mens Season')
plt.legend()

plt.figure(3)
plt.plot(tn, 'go', ms=4, label='True Negatives')
plt.ylabel('Win %')
plt.xlabel('Sequential Games')
plt.xlim([0,truePositive + trueNegative])
plt.ylim([0,1.2])
plt.title('Predicted Win Percentages of True Negatives on the 2014-2015 NCAA Mens Season')
plt.legend()

plt.figure(4)
plt.plot(fn, 'mo', ms=4, label='False Negatives')
plt.ylabel('Win %')
plt.xlabel('Sequential Games')
plt.xlim([0,falseNegative + falsePositive])
plt.ylim([0,1.2])
plt.title('Predicted Win Percentages of False Negatives on the 2014-2015 NCAA Mens Season')
plt.legend()

# Time to put these suckers on one graph (normalized for length)
trueXAxis = []
falseXAxis = []
for i in range(truePositive + trueNegative):
    trueXAxis += [i / (truePositive + trueNegative)]
for i in range(falsePositive + falseNegative):
    falseXAxis += [i / (falsePositive + falseNegative)]

plt.figure(5)
plt.plot(trueXAxis,tp, 'bo', ms=4, label='True Positives')
plt.plot(falseXAxis,fp, 'ro', ms=4, label='False Positives')
plt.plot(trueXAxis,tn, 'go', ms=4, label='True Negatives')
plt.plot(falseXAxis,fn, 'mo', ms=4, label='False Negatives')
plt.ylabel('Win %')
plt.xlabel('Normalized Season Length')
plt.xlim([0,1])
plt.ylim([0,1.2])
plt.title('Predicted Win Percentages on the 2014-2015 NCAA Mens Season')
plt.legend()

plt.figure(6)
plt.plot(trueXAxis,tp, 'bo', ms=8, label='True Positives')
plt.plot(falseXAxis,fp, 'ro', ms=8, label='False Positives')
plt.plot(trueXAxis,tn, 'go', ms=8, label='True Negatives')
plt.plot(falseXAxis,fn, 'mo', ms=8, label='False Negatives')
plt.ylabel('Win %')
plt.xlabel('Normalized Season Length')
plt.xlim([0,1])
plt.ylim([0,1.2])
plt.title('Predicted Win Percentages on the 2014-2015 NCAA Mens Season with Bigger Dots')
plt.legend()

plt.show()