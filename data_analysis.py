import pandas as pd
from scipy.spatial.distance import cosine
import numpy as np

def recommend(targetUser):
    # See example here: http://tungwaiyip.info/2012/Collaborative%20Filtering.html

    df = pd.read_csv("frappe.csv", "\t")
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

    # Compute pairwise correlation
    # sim_0 =  ratingP.corrwith(ratingUser)

    # Include only items not consumed by user yet and remove rows for user
    notConsumed = (ratingUser[ratingList.item] == 0).values # True/False array
    ratingListNew = ratingList[notConsumed & (ratingList.user != targetUser)]
    ratingListNew['similarity'] = ratingListNew['user'].map(cosine_sim.get)
    ratingListNew['sim_rating'] = ratingListNew.similarity * ratingListNew.cnt

    recommendation = ratingListNew.groupby('item').apply(lambda row: row.sim_rating.sum() / row.similarity.sum())
    return recommendation.sort_values(ascending=False)[:10]


print recommend(936)