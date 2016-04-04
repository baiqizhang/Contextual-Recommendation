import csv
import numpy as np

user_set = set()
item_set = set()

user_rate_list = {}  # map (uid) -> [(iid,rating,loc,time)]


# similarity
def cosine_sim(user_1, user_2, time='ANY', location='ANY'):
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
        if (time == 'ANY' or time == item[2]) and (location == 'ANY' or location == item[3]):
            score_1[item[0]] = int(item[1])
    for item in user_rate_list[user_2]:
        if (time == 'ANY' or time == item[2]) and (location == 'ANY' or location == item[3]):
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


def recommend(user, time='ANY', location='ANY'):
    """
    recommendation algorithm with pre-filtering
    :param user: user id
    :param time: ANY or a time
    :param location: ANY or a location
    :return: list of (recommendation item, score)
    """
    sum = 0
    for other_user in user_rate_list:
        if user == other_user:
            continue
        sum += cosine_sim(user, other_user,time,location)
        # print user,other_user,cosine_sim(user, other_user,time,location)

    score_final = {} # = sum{score/count}
    for other_user in user_rate_list:
        if user == other_user:
            continue
        k = cosine_sim(user, other_user, time, location) / sum

         # average when user has more than one rating for an item
        score = {}
        count = {}

        for item in user_rate_list[other_user]:
            # pre filtering
            if (time == 'ANY' or time == item[2]) and (location == 'ANY' or location == item[3]):
                id = item[0]
                rate = float(item[1])
                # if id == 'tt0266543':
                #     print other_user, k * rate,rate, k,k*sum,sum
                if score.has_key(id):
                    score[id] += k * rate
                    count[id] += 1
                else:
                    score[id] = k * rate
                    count[id] = 1
        for id in score:
            if score_final.has_key(id):
                score_final[id] += score[id]/count[id]
            else:
                score_final[id] = score[id]/count[id]

    # soring
    result = []
    for id in score_final:
        result.append((id, score_final[id]))
        # print id,":",score[id]
    result.sort(key=lambda x: x[1], reverse=True)
    return result

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
            if location != 'NA' and time != 'NA':
                if user_rate_list.has_key(userid):
                    user_rate_list[userid].append((itemid, rating, time, location))
                else:
                    user_rate_list[userid] = [(itemid, rating, time, location)]

    # print cosine_sim('1032', '1116')
    print 'user count =',len(user_set)
    print 'item count =',len(item_set)

    print recommend('1032')
    print user_rate_list['1032']
