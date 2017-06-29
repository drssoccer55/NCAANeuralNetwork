import sys, getopt, csv
import matplotlib.pyplot as plt
import random

numPredictions = 0
totalPoints = 0

for i in range(1,5500):
    with open('C:\\Users\\Douglas\\Documents\\Visual Studio 2012\\Projects\\NCAABasketball\\NCAABasketball\\2014-2015\game' + str(i) + '.txt', 'r') as csvfile:
        content = csv.reader(csvfile)
        gameStat = list(content)
        team1 = gameStat[0]
        team2 = gameStat[1]
        totalPoints += float(team1[22]) + float(team2[22])
        numPredictions += 2
            
average = float(totalPoints) / float(numPredictions)  
print("NumPredictions: ", numPredictions)
print("Average Points: ", average)


scores = []
absDifferenceTotal = 0.0
# Now use that to make a prediction on each game and collect absoulte difference
for i in range(1,5500):
    with open('C:\\Users\\Douglas\\Documents\\Visual Studio 2012\\Projects\\NCAABasketball\\NCAABasketball\\2014-2015\game' + str(i) + '.txt', 'r') as csvfile:
        content = csv.reader(csvfile)
        gameStat = list(content)
        team1 = gameStat[0]
        team2 = gameStat[1]
        scores += [float(team1[22])] + [float(team2[22])]
        absDifferenceTotal += abs(float(team1[22]) - average) + abs(float(team2[22]) - average)

print("Average Abs Difference: ", absDifferenceTotal / float(numPredictions))

plt.figure(1)
plt.plot(scores, 'bo', ms=4)
# draw horizaontal line for average
plt.plot([0, numPredictions], [average, average], 'r-', lw=4, label='Average')
plt.ylabel('Point Scored')
plt.xlabel('Sequential Games')
plt.title('Points Scored by Teams in the 2014-2015 NCAA Mens Basketball Season')
plt.legend()
plt.xlim([0,numPredictions])

# Now make a pretty graph using jitter.
jitterScores = []
for i in range(len(scores)):
    jitter = random.random() - 0.5 # Jitter between -0.5 and 0.5!
    jitterScores += [scores[i] + jitter]

plt.figure(2)
plt.plot(jitterScores, 'bo', ms=4)
# draw horizaontal line for average
plt.plot([0, numPredictions], [average, average], 'r-', lw=4, label='Average')
plt.ylabel('Point Scored')
plt.xlabel('Sequential Games')
plt.title('Points Scored by Teams in the 2014-2015 NCAA Mens Basketball Season with Jitter between +/- 0.5')
plt.legend()
plt.xlim([0,numPredictions])

plt.show()