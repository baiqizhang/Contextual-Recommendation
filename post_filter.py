import csv
import numpy as np
from collections import defaultdict

user_set = set()
item_set = set()

user_rate_list = {}  # map (uid) -> [(iid,rating,loc,time)]

def cosine_sim(user_1, user_2):
    """
    cosine similarity between users using pre-filtering
    :return: a float : score
    """

    score_1 = {}
    score_2 = {}
    N1 = 0
    N2 = 0
    N = 0
    for item in user_rate_list[user_1]:
        score_1[item[0]] = int(item[1])
    for item in user_rate_list[user_2]:
        score_2[item[0]] = int(item[1])

    # in case of duplication:
    for id in score_1:
        N1 += score_1[id] * score_1[id]
    for id in score_2:
        N2 += score_2[id] * score_2[id]

    # calculate cosine
    for id in score_1:
        if score_2.has_key(id):
            N += score_1[id] * score_2[id]
            # print id, score_1[id], score_2[id]
    if N1 == 0 or N2 == 0:
        return 0
    return N / (np.sqrt(N1) * np.sqrt(N2))


def recommend(user, time, location):
    """
    recommendation algorithm with pre-filtering
    :param user: user id
    :param time: ANY or a time
    :param location: ANY or a location
    :return: list of (recommendation item, score)
    """

    # Calculate user similarity
    sum = 0
    cosine_sim_list = {}
    for other_user in user_rate_list:
        if user == other_user:
            continue
        sim = cosine_sim(user, other_user)
        cosine_sim_list[other_user] = sim
        sum += sim

    score_final = {} # = sum{score/count}
    for other_user in user_rate_list:
        if user == other_user:
            continue

        # average when user has more than one rating for an item
        score = {}
        count = {}

        for item in user_rate_list[other_user]:
            itemid = item[0]
            rating = float(item[1])
            # if id == 'tt0266543':
            #     print other_user, k * rate,rate, k,k*sum,sum
            if itemid in score:
                score[itemid] += rating
                count[itemid] += 1
            else:
                score[itemid] = rating
                count[itemid] = 1

        # Add average rating, adjusted by k which accounts for similarity
        k = cosine_sim_list[other_user] / sum
        for itemid in score:
            if itemid in score_final:
                score_final[itemid] += k * score[itemid]/count[itemid]
            else:
                score_final[itemid] = k * score[itemid]/count[itemid]

    # Post-filtering
    result = {}
    post_relevant = defaultdict(float)
    for itemid in score_final:
        result[itemid] = score_final[itemid]

    for other_user in user_rate_list:
        if user == other_user:
            continue
        for row in user_rate_list[other_user]:
            if row[0] in result and row[2] == time and row[3] == location:
                post_relevant[row[0]] += 1

    # Construct results and sorting
    n = len(user_set)  # Alternative: calculate number of users who consumed item i?
    result_update = []
    for itemid in result:
        result_update.append((itemid, result[itemid]*post_relevant[itemid]/n))

    result_update.sort(key=lambda x: x[1], reverse=True)
    return result_update

    # result.sort(key=lambda x: x[1], reverse=True)
    # return result

# main
if __name__ == '__main__':
    with open('ratings.txt', 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            location = row['Location']
            time = row['Time']
            userid = row['userid']
            itemid = row['itemid']
            rating = row['rating']
            user_set.add(userid)
            item_set.add(itemid)
            # only use data where time and location are both available
            if user_rate_list.has_key(userid):
                user_rate_list[userid].append((itemid, rating, time, location))
            else:
                user_rate_list[userid] = [(itemid, rating, time, location)]

    print 'user count =',len(user_set)
    print 'item count =',len(item_set)

    print recommend('1032', 'Weekday', 'Home')
    print user_rate_list['1032']