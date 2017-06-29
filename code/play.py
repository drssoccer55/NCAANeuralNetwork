import model
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
totalAbsoluteDifference = 0
closestGuess = 9999999
furthestGuess = 0
predictions = []
actuals = []
absDifferences = []

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
            
            # Predict score for first team
            x_data = [team1stats + team2stats + diff1]
            team1ActualScore = float(team1[22])
            team1ScorePrediction = model.y.eval(feed_dict={model.x: x_data, model.keep_prob: 1.0})[0] # Get output vector from model
            # Predict score for second team
            x_data = [team2stats + team1stats + diff2]
            team2ActualScore = float(team2[22])
            team2ScorePrediction = model.y.eval(feed_dict={model.x: x_data, model.keep_prob: 1.0})[0] # Get output vector from model

            # Analyze!!!
            predictableGames += 1
            if (team1ActualScore - team2ActualScore) > 0.0 and (team1ScorePrediction - team2ScorePrediction) > 0:
                correctPrediction += 1
            elif (team1ActualScore - team2ActualScore) < 0.0 and (team1ScorePrediction - team2ScorePrediction) < 0:
                correctPrediction += 1
            else:
                wrongPrediction += 1
                
            t1Difference = abs(team1ScorePrediction - team1ActualScore)
            t2Difference = abs(team2ScorePrediction - team2ActualScore)
            totalAbsoluteDifference += t1Difference + t2Difference
            furthestGuess = max(furthestGuess, t1Difference)
            furthestGuess = max(furthestGuess, t2Difference)
            closestGuess = min(closestGuess, t1Difference)
            closestGuess = min(closestGuess, t2Difference)
            predictions += [team1ScorePrediction] + [team2ScorePrediction]
            actuals += [team1ActualScore] + [team2ActualScore]
            absDifferences += [abs(team1ScorePrediction - team1ActualScore)] + [abs(team2ScorePrediction - team2ActualScore)]
            
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
print("Average Absolute Difference: ", totalAbsoluteDifference / (predictableGames * 2.0))
print("Max Absolute Difference: ", furthestGuess)
print("Min Absolute Difference: ", closestGuess)

plt.figure(1)
plt.plot(actuals, 'bo', ms=4, label='Actual')
plt.plot(predictions, 'ro', ms=4, label='Prediction')
plt.ylabel('Points Scored')
plt.xlabel('Sequential Games')
plt.xlim([0,(predictableGames * 2)])
plt.title('Points and Predictions on the 2014-2015 NCAA Mens Season')
plt.legend()
plt.figure(2)
plt.plot(absDifferences, 'ro', ms=4)
plt.ylabel('Absolute Difference')
plt.xlabel('Sequential Games')
plt.xlim([0,(predictableGames * 2)])
plt.title('Absolute Difference of Prediction and Actual on the 2014-2015 NCAA Mens Season')

# Now make a pretty graph using jitter.
jitterScores = []
for i in range(len(actuals)):
    jitter = random.random() - 0.5 # Jitter between -0.5 and 0.5!
    jitterScores += [actuals[i] + jitter]

plt.figure(3)
plt.plot(jitterScores, 'bo', ms=4, label='Actual +/- 0.5 Jitter')
plt.plot(predictions, 'ro', ms=4, label='Prediction')
plt.ylabel('Points Scored')
plt.xlabel('Sequential Games')
plt.xlim([0,(predictableGames * 2)])
plt.title('Points and Predictions on the 2014-2015 NCAA Mens Season with Jitter')
plt.legend()

plt.show()