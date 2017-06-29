import team_stats, csv, sys, getopt
import model
import tensorflow as tf
import numpy as np

LEARNING_RATE = 1e-4 # Need to fiddle with this to find what works well

# Get arguments for input model or output
argv = sys.argv[1:]
inputmodel = None
outputmodel = '.\model.ckpt'
try:
    opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
except getopt.GetoptError:
    print('train.py -i <inputmodel> -o <outputmodel>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('train.py -i <inputmodel> -o <outputmodel>')
        sys.exit()
    elif opt in ("-i", "--ifile"):
        inputmodel = ".\\" + arg + ".ckpt"
    elif opt in ("-o", "--ofile"):
        outputmodel = ".\\" + arg + ".ckpt"

# Start session
sess = tf.InteractiveSession()

# Learning Functions
L2NormConst = 0.001
train_vars = tf.trainable_variables()
loss = tf.reduce_mean(tf.square(tf.sub(model.y_, model.y))) + tf.add_n([tf.nn.l2_loss(v) for v in train_vars]) * L2NormConst
train_step = tf.train.AdamOptimizer(1e-4).minimize(loss)

sess.run(tf.global_variables_initializer())

# Load Model
if inputmodel is not None:
    saver = tf.train.Saver()
    saver.restore(sess, inputmodel) # Restore if model exists

# Training loop variables
epochs = 100
batch_size = 50
num_samples = 24600 # Update this with more training examples
step_size = int(num_samples / batch_size)

for epoch in range(100):
    
    teams = {}
    x_data = []
    y_data = []
    counter = 0
    for i in range(1,5517):
        #if i == 3286: # Turns out this game got postponed due to a leaky roof and now nobody has the data except for the final score
        #    continue
        with open('C:\\Users\\Douglas\\Documents\\Visual Studio 2012\\Projects\\NCAABasketball\\NCAABasketball\\2015-2016\game' + str(i) + '.txt', 'r') as csvfile:
            content = csv.reader(csvfile)
            gameStat = list(content)
            team1 = gameStat[0]
            team2 = gameStat[1]
            if team1[0] in teams and team2[0] in teams:
                # Get stats of both teams
                team1stats = teams[team1[0]].getStatVect()
                team2stats = teams[team2[0]].getStatVect()
                # Calculate differences between stats for extra feature
                diff1 = []
                diff2 = []
                for j in range(len(team1stats)):
                    diff1 += [team1stats[j] - team2stats[j]]
                    diff2 += [team2stats[j] - team1stats[j]]
                    
                x_data += [team1stats + team2stats + diff1]
                y_data += [[float(team1[22])]]
                x_data += [team2stats + team1stats + diff2]
                y_data += [[float(team2[22])]]
                if i == 5516 or len(x_data) == 50:
                    train_step.run(feed_dict={model.x: x_data, model.y_: y_data, model.keep_prob: 0.8})

                    loss_value = loss.eval(feed_dict={model.x: x_data, model.y_: y_data, model.keep_prob: 1.0})
                    print("epoch: %d step: %d loss: %g"%(epoch, counter, loss_value))
                        
                    x_data = []
                    y_data = []
                    counter += 1

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

# Save the Model
saver = tf.train.Saver()
saver.save(sess, outputmodel)
