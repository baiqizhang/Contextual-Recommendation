import pandas as pd
import numpy as np

def main():
    # See example here: http://tungwaiyip.info/2012/Collaborative%20Filtering.html

    df = pd.read_csv("frappe.csv", "\t")
    print df
    df.drop(df.columns[range(3,11)], axis=1, inplace=True)
    rating = df.groupby(["user", "item"])["cnt"].sum().reset_index()
    ratingP =  rating.pivot_table("cnt", "item", "user")

    rating0 = ratingP[0]
    sim_0 =  ratingP.corrwith(rating0)

    rating_c = rating[(rating0[rating.item].isnull().values) & (rating.user != 0)]
    print rating_c
    rating_c['similarity'] = rating_c['user'].map(sim_0.get)
    print rating_c
    rating_c['sim_rating'] = rating_c.similarity * rating_c.cnt

    recommendation = rating_c.groupby('item').apply(lambda s: s.sim_rating.sum() / s.similarity.sum())
    print recommendation.sort_values(ascending=False)


main()