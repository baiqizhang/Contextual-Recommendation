import pandas as pd
from scipy.spatial.distance import cosine
import numpy as np

# See example here: http://tungwaiyip.info/2012/Collaborative%20Filtering.html
def recommend(df, targetUser):
    df.drop(df.columns[range(3,11)], axis=1, inplace=True)
    ratingList = df.groupby(["user", "item"])["cnt"].sum().reset_index()
    ratingMatrix = ratingList.pivot_table("cnt", "item", "user")
    ratingMatrix = ratingMatrix.fillna(0)

    # Compute Cosine Similarity
    ratingUser = ratingMatrix[targetUser]
    cosine_sim = []
    for cIndex in ratingMatrix.columns:
        cosine_sim.append(1 - cosine(ratingUser, ratingMatrix[cIndex]))
    cosine_sim = pd.Series(cosine_sim)

    # Compute pairwise correlation (example approach)
    # sim_0 =  ratingP.corrwith(ratingUser)

    # Include only items not consumed by user yet and remove rows for user
    notConsumed = (ratingUser[ratingList.item] == 0).values # True/False array
    ratingListNew = ratingList[notConsumed & (ratingList.user != targetUser)]
    ratingListNew.loc[:,'similarity'] = ratingListNew.loc[:,'user'].map(cosine_sim.get)
    ratingListNew.loc[:,'sim_rating'] = ratingListNew.loc[:,'similarity'] * ratingListNew.loc[:,'cnt']

    recommendation = ratingListNew.groupby('item').apply(lambda row: row.sim_rating.sum() / row.similarity.sum())
    return recommendation.sort_values(ascending=False)[:10]

def recommendPreFilter(df, targetUser, contexts, contextValues):

    # Filter out irrelevant columns
    criteria = contexts + ["user", "item", "cnt"]
    for column in df.columns:
        if column not in criteria:
            df.drop(column, axis=1, inplace=True)

    # Retain rows that match the context values
    n = len(contexts)
    for i in xrange(n):
        df = df[df[contexts[i]] == contextValues[i]]

    # Aggregate rows with same values
    ratingList = df.groupby(["user", "item"])["cnt"].sum().reset_index()
    ratingMatrix = ratingList.pivot_table("cnt", "item", "user")
    ratingMatrix = ratingMatrix.fillna(0)

    # Cannot recommend if user not in the filtered list
    if targetUser not in ratingMatrix.columns.tolist():
        raise Exception("User not in filtered list")

    # Compute Cosine Similarity
    ratingUser = ratingMatrix[targetUser]
    cosine_sim = []
    for cIndex in ratingMatrix.columns:
        cosine_sim.append(1 - cosine(ratingUser, ratingMatrix[cIndex]))
    cosine_sim = pd.Series(cosine_sim)

    # Include only items not consumed by user yet and remove rows for user
    notConsumed = (ratingUser[ratingList.item] == 0).values # True/False array
    ratingListNew = ratingList[notConsumed & (ratingList.user != targetUser)]
    ratingListNew.loc[:,'similarity'] = ratingListNew.loc[:,'user'].map(cosine_sim.get)
    ratingListNew.loc[:,'sim_rating'] = ratingListNew.loc[:,'similarity'] * ratingListNew.loc[:,'cnt']

    recommendation = ratingListNew.groupby('item').apply(lambda row: row.sim_rating.sum() / row.similarity.sum())
    return recommendation.sort_values(ascending=False)[:10]

def generateData(filename, trainFrac):
    df = pd.read_csv(filename, "\t")
    df_train = df.sample(frac = trainFrac)
    df_test = df.loc[~df.index.isin(df_train.index)]
    return df_train, df_test

df_train, df_test = generateData("frappe.csv", 0.8)
print recommend(df_train.copy(), 2)
print recommendPreFilter(df_train.copy(), 2, ["homework", "isweekend"], ["home", "weekend"])