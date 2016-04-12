import pandas as pd
from scipy.spatial.distance import cosine
import numpy as np

# To-do: calculate similarity matrix first

# See example here: http://tungwaiyip.info/2012/Collaborative%20Filtering.html
def recommend(df, targetUser, top=10):
    ratingMatrix = df.pivot_table("cnt", "item", "user")
    ratingMatrix = ratingMatrix.fillna(0)

    # Compute Cosine Similarity
    ratingUser = ratingMatrix[targetUser]
    cosine_sim = pd.Series()
    for cIndex in ratingMatrix.columns:
        cosine_sim.set_value(cIndex, 1 - cosine(ratingUser, ratingMatrix[cIndex]))

    # Compute pairwise correlation (example approach)
    # sim_0 =  ratingP.corrwith(ratingUser)

    # Include only items not consumed by user yet and remove rows for user
    notConsumed = (ratingUser[df.item] == 0).values # True/False array
    ratingListNew = df[notConsumed & (df.user != targetUser)]
    ratingListNew.loc[:,'similarity'] = ratingListNew.loc[:,'user'].map(cosine_sim.get)
    ratingListNew.loc[:,'sim_rating'] = ratingListNew.loc[:,'similarity'] * ratingListNew.loc[:,'cnt']

    recommendation = ratingListNew.groupby('item').apply(lambda row: row.sim_rating.sum() / row.similarity.sum())
    recommendation = recommendation.sort_values(ascending=False)[:top]
    return recommendation

def recommendPreFilter(df, targetUser, contexts, contextValues, top=10):
    ratingMatrix = df.pivot_table("cnt", "item", "user")
    ratingMatrix = ratingMatrix.fillna(0)

    # Cannot recommend if user not in the filtered list
    if targetUser not in ratingMatrix.columns.tolist():
        raise Exception("User not in filtered list")

    # Compute Cosine Similarity
    ratingUser = ratingMatrix[targetUser]
    cosine_sim = pd.Series()
    for cIndex in ratingMatrix.columns:
        cosine_sim.set_value(cIndex, 1 - cosine(ratingUser, ratingMatrix[cIndex]))

    # Include only items not consumed by user yet and remove rows for user
    notConsumed = (ratingUser[df.item] == 0).values # True/False array
    ratingListNew = df[notConsumed & (df.user != targetUser)]
    ratingListNew.loc[:,'similarity'] = ratingListNew.loc[:,'user'].map(cosine_sim.get)
    ratingListNew.loc[:,'sim_rating'] = ratingListNew.loc[:,'similarity'] * ratingListNew.loc[:,'cnt']

    recommendation = ratingListNew.groupby('item').apply(lambda row: row.sim_rating.sum() / row.similarity.sum())
    recommendation = recommendation.sort_values(ascending=False)[:top]
    return recommendation

def recommendPostFilter(df_2D, df, targetUser, contexts, contextValues, top=10):
    recommendation = recommend(df_2D, targetUser, top*10) # Get ten times the results for reordering

    # Filter out irrelevant columns
    criteria = contexts + ["user", "item", "cnt"]
    for column in df.columns:
        if column not in criteria:
            df.drop(column, axis=1, inplace=True)

    # Retain rows that match the context values
    n = len(contexts)
    for i in xrange(n):
        df = df[df[contexts[i]] == contextValues[i]]
    df = df.groupby(["user", "item"])["cnt"].sum().reset_index()
    ratingMatrix = df.pivot_table("cnt", "item", "user")
    ratingMatrix = ratingMatrix.fillna(0)

    # Compute Cosine Similarity
    ratingUser = ratingMatrix[targetUser]
    cosine_sim = pd.Series()
    for cIndex in ratingMatrix.columns:
        cosine_sim.set_value(cIndex, 1 - cosine(ratingUser, ratingMatrix[cIndex]))

    # Adjust prediction values by contextual probability
    numSim = 80 # assumed neighborhood size
    cosine_sim = cosine_sim.sort_values(ascending=False)[1:numSim] # remove itself
    df_sim = df[df["user"].isin(cosine_sim.index)] # only include similar users
    itemCount = pd.value_counts(df_sim["item"].values)

    # for (item, prediction) in recommendation.iteritems():
    #     numRelevant = df_sim[(df_sim["item"] == item)].shape[0]
    #     # Weight method
    #     recommendation.set_value(item, prediction*numRelevant/numSim)
    #
    #     # Filter method
    #     # if numRelevant == 0:
    #     #     recommendation.set_value(item, 0)

    recommendation = recommendation.to_frame("oldScore")
    recommendation.loc[:,"newScore"] = recommendation.index
    recommendation.loc[:,"newScore"] = recommendation.loc[:,"newScore"].map(itemCount)
    # Weight method
    recommendation.loc[:,"newScore"] = recommendation.loc[:,"oldScore"]* \
                                       recommendation.loc[:,"newScore"]/numSim
    # Filter method
    # recommendation.loc[:,"newScore"] = recommendation.apply(filter, axis = 1)
    recommendation = recommendation.loc[:,"newScore"].sort_values(ascending=False)[:top]
    return recommendation

def filter(row):
    if row["newScore"] > 0:
        return row["oldScore"]
    else:
        return 0

def generateData(filename, trainFrac):
    df = pd.read_csv(filename, "\t")
    df.drop(df.columns[range(3,11)], axis=1, inplace=True)
    df = df.groupby(["user", "item"])["cnt"].sum().reset_index()

    df_train = df.sample(frac = trainFrac)
    df_test = df.loc[~df.index.isin(df_train.index)]
    return df_train, df_test

def generateDataPreFilter(filename, trainFrac, contexts, contextValues):
    df = pd.read_csv(filename, "\t")

    # Filter out irrelevant columns
    criteria = contexts + ["user", "item", "cnt"]
    for column in df.columns:
        if column not in criteria:
            df.drop(column, axis=1, inplace=True)

    # Retain rows that match the context values
    n = len(contexts)
    for i in xrange(n):
        df = df[df[contexts[i]] == contextValues[i]]

    df = df.groupby(["user", "item"])["cnt"].sum().reset_index()

    df_train = df.sample(frac = trainFrac)
    df_test = df.loc[~df.index.isin(df_train.index)]
    return df_train, df_test

df_train, df_test = generateData("frappe.csv", 1)
df_train_prefilter, df_prefilter = generateDataPreFilter("frappe.csv", 1, ["homework", "isweekend"], ["home", "workday"])

print recommend(df_train.copy(), 2)
print recommendPreFilter(df_train_prefilter.copy(), 2, ["homework", "isweekend"], ["home", "workday"])
print recommendPostFilter(df_train.copy(), pd.read_csv("frappe.csv", "\t"), 2, ["homework", "isweekend"], ["home", "workday"])
