import csv

class team_stats:
    def __init__(self, initialVector):
        self.teamName = initialVector[0]
        # MP	FG	FGA	FG%	2P	2PA	2P%	3P	3PA	3P%	FT	FTA	FT%	ORB	DRB	TRB	AST	STL	BLK	TOV	PF	PTS
        # MP	TS%	eFG%	3PAr	FTr	ORB%	DRB%	TRB%	AST%	STL%	BLK%	TOV%	USG%	ORtg	DRtg
        # Add categories for GP, Wins, Winstreak, Losestreak
        # Skipped usage % since always 100 and also don't duplicate count minutes played
        self.r = initialVector[1:23] + initialVector[24:35] + initialVector[36:38] + [1.0,0.0,0.0,0.0]
        
    def display(self):
        print(self.teamName)
        print(self.r)
        # print(len(self.r))
        
    def win(self):
        self.r[36] += 1.0
        self.r[37] += 1.0
        self.r[38] = 0.0
    
    def lose(self):
        self.r[37] = 0.0
        self.r[38] += 1.0

    # Updates everything except win/lose statistics which need to be done as an extra step!
    def updateStats(self, statVector):
        convertVector = statVector[1:23] + statVector[24:35] + statVector[36:38] + [1.0,0.0,0.0,0.0]
        for i in range(len(self.r)):
            self.r[i] = float(self.r[i]) + float(convertVector[i])

    # Return all averages except number of minutes, games played, wins, winstreak, losestreak    
    def getStatVect(self):
        statVector = [float(self.r[0])]
        for i in range(1,35):
            statVector += [float(self.r[i]) / float(self.r[35])]
        for i in range(35,39):
            statVector += [float(self.r[i])]
        # Oh wait acutally need to fix FG 2p 3p FT percentages
        statVector[3] = float(self.r[1]) / float(self.r[2])
        statVector[6] = float(self.r[4]) / float(self.r[5])
        statVector[9] = float(self.r[7]) / float(self.r[8])
        statVector[12] = float(self.r[10]) / float(self.r[11])
        return statVector


# This is just for class testing purposes 5517

'''
teams = {}
for i in range(1,5390):
    if i == 3286: # Turns out this game got postponed due to a leaky roof and now nobody has the data except for the final score
        continue
    with open('C:\\Users\\Douglas\\Documents\\Visual Studio 2012\\Projects\\NCAABasketball\\NCAABasketball\\2016-2017\game' + str(i) + '.txt', 'r') as csvfile:
        content = csv.reader(csvfile)
        gameStat = list(content)
        team1 = gameStat[0]
        team2 = gameStat[1]
        if team1[0] in teams and team2[0] in teams:
            #print("Both teams found")
            teams[team1[0]].updateStats(team1)
            teams[team2[0]].updateStats(team2)
        else:
            # First add team1 to dictionary
            if team1[0] in teams:
                teams[team1[0]].updateStats(team1)
                #print("Updating team: " + str(team1[0]))
            else:
                teams[team1[0]] = team_stats(team1)
            # Now add team2 to dictionary
            if team2[0] in teams:
                teams[team2[0]].updateStats(team2)
                #print("Updating team: " + str(team2[0]))
            else:
                teams[team2[0]] = team_stats(team2)

        if team1[22] <= team2[22]:
            teams[team1[0]].lose()
            teams[team2[0]].win()
        else:
            teams[team1[0]].win()
            teams[team2[0]].lose()
        
        #if i == 5516:
            #print(teams[team1[0]].getStatVect())
            
        #print(teams)
        print(i)
        #print(teams[team1[0]].getStatVect())
        #print(teams[team2[0]].getStatVect())
'''


