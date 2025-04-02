# %%
'''
A bad little implementation of preferential voting for whatever use case you have, using the Instant-Runoff algorithm.
'''
import numpy as np 
import matplotlib.pyplot as plt

class party(object):
    def __init__(self, name, colour, desc=""):
        self.name = name
        self.desc = desc
        self.colour = colour
        
        
class ballot(object):
    def __init__(self, parties, preferences={}):
        self.parties = parties
        self.preferences = preferences
    
    def cast_votes(self):
        print(f"The choices are {[print(party.name) for party in self.parties]}")
        votes = input("Please enter your <COMMA SEPARATED> numerical preferences, 1 being highest, etc:")
        numbers = [float(value) for value in votes.split(',')]
        for i, party in enumerate(self.parties):
            self.preferences[party.name] = numbers[i]
        
    
    def obtain_votes(self):
        if len(self.preferences) == 0:
            raise ValueError("The votes have not yet been cast for this ballot.")
        else:
            return self.preferences
        


class election(object):
    def __init__(self, ballots):
        '''
        Parameters
        ----------
        parties : list of party objects
        ballots : list of ballot objects
        '''
        self.ballots = ballots
        self.tot_votes = len(ballots)
        self.parties = ballots[0].parties
        
        self.n_parties = len(self.parties)
        self.iterations = 0
        
        self.all_standings = []
        self.current_standing = {}
        for party in self.parties:
            self.current_standing[party.name] = 0
        
        self.calculated_result = False
    
    def distribute_votes(self, relevant_parties):
        party_counts = {party:0 for party in relevant_parties}
        for i in range(len(self.ballots)):
            preferences = self.ballots[i].obtain_votes()
            relevant_preferences = {party: preferences[party] for party in relevant_parties}
            highest_party = min(relevant_preferences, key=relevant_preferences.get)   # gets the dictionary key name corresponding to the lowest value (highest preference)
            party_counts[highest_party] += 1
        return party_counts
    
    def calculate_standing(self):
        old_standing = self.current_standing.copy()
        current_standing = {}
        relevant_parties = list(old_standing.keys())[:self.n_parties - self.iterations]      # assumes list is sorted in descending order of most votes
        
        current_standing = self.distribute_votes(relevant_parties)
        # now sort them in terms of descending popularity: https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        current_standing = {party: votes for party, votes in sorted(current_standing.items(), key=lambda item: item[1])[::-1]} 
        
        return current_standing
        
        
        
    def calculate_result(self):
        majority_party = list(self.current_standing.keys())[0]
        while self.current_standing[majority_party] <= self.tot_votes / 2:
            new_standing = self.calculate_standing()
            self.current_standing = new_standing
            self.all_standings.append(self.current_standing)
            self.iterations += 1
            majority_party = list(self.current_standing.keys())[0]
        
        self.calculated_result = True
        
    def sankey_coords(self, x1, y1, x2, y2):
        X = np.linspace(0, 2, 100)
        Y = -np.exp(-X**2.8)
        Y = (Y+1) * (y2 - y1) + y1
        return np.linspace(x1, x2, 100), Y
        
    def alluvian_diagram(self):
        if not self.calculated_result:
            self.calculate_result()
        
        width = 0.4
        
        fig, ax = plt.subplots(figsize=(self.iterations + 1, 5))
        ax.set_axis_off()
        all_bars = []
        for i in range(self.iterations):
            standing = self.all_standings[i]
            standing_parties = list(standing.keys())[::-1]
            iter_bars = []
            height = 0
            sankey_height = 0
            if i == 0:
                previous_colour = 'r'
            else:
                previous_colour = next_colour
            for j in range(len(standing_parties)):
                for party in self.parties:
                    if standing_parties[j] == party.name:
                        current_party = party
                colour = current_party.colour
                bar_height = standing[standing_parties[j]]
                if i == 0:
                    ax.text(-0.3, height + bar_height/3, standing_parties[j], color=colour, horizontalalignment='right')
                elif i > 0:
                    previous_votes = self.all_standings[i - 1][standing_parties[j]]
                    delta_votes = bar_height - previous_votes
                    if j == 0:
                        ax.fill_between([i-1 + width/2 + 0.015, i - width/2], delta_votes, 0, color=previous_colour, ec=None)
                    else:
                        X, Y = self.sankey_coords(i-1 + width/2 + 0.015, sankey_height, i - width/2, height)
                        ax.fill_between(X, Y, Y + delta_votes, color=previous_colour, ec=None)
                    sankey_height += delta_votes
                        
                iter_bars.append(ax.bar(i, bar_height, width=width, bottom=height, color=colour, ec='k'))
                height += bar_height
                
                if j == 0:
                    next_colour = colour
        return fig
                
        
        

def main():
    party_names = ['Liberal', 'Independent', 'Labor', 'Greens', 'United Aus', 'One Nation']
    party_colours = ['tab:blue', 'tab:cyan', 'tab:red', 'tab:green', 'gold', 'tab:orange']
    party_probs = {'Liberal': 0.35, 'Independent':0.25, 'Labor':0.2, 'Greens':0.11, 'United Aus':0.06, 'One Nation':0.04}
    parties = [party(name, colour) for name, colour in zip(party_names, party_colours)]
    
    all_ballots = []
    for i in range(10000):
        preferences = {}
        valid_parties = party_names.copy()
        random_nums = np.random.uniform(size=len(party_names)-1)
        
        for k in range(len(party_names)-1):
            j = 0
            mult = sum(party_probs[party] for party in valid_parties)
            while True:
                if random_nums[k] < sum(party_probs[valid_parties[jj]] for jj in range(j)) / mult:
                    preferences[valid_parties[j-1]] = k+1
                    break
                j += 1
            valid_parties.remove(valid_parties[j-1])
        preferences[valid_parties[0]] = len(party_names)
        all_ballots.append(ballot(parties, preferences=preferences))
    
    this_election = election(all_ballots)
    this_election.calculate_result()
    print(this_election.all_standings)
    
    fig = this_election.alluvian_diagram()
    fig.savefig('diagram.png', dpi=400)
        

if __name__ == "__main__":
    main()


# %%
