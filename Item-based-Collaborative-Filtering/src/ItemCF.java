import java.util.PriorityQueue;
import java.util.Queue;

/* 
 * 
 * Item-based CF
 * 
 * Input: userid
 * Output: top n items recommended for the user 
 * 
 * 
 */


public class ItemCF {

	public final static int K = 100;
	public final static int N = 10;
	
	public int[][] rating;//rating[x][y]: user x gives a score to item y
	
	
	/*
	 * Step 1. getAdjustedCosine -- Adjusted Cosine Similarity Computation
	 * 
	 * - Why choose Adjusted Cosine Similarity Computation rather than basic cosine similarity computation? 
	 * - Take the difference in rating scale between different users into account.
	 * 
	 * - Input:
	 * item i, item j
	 * 
	 * - Output:
	 * Similarity between item i and item j
	 * 
	 */	
	
	public double getAdjustedCosine(int item_i, int item_j) {
		
		int len = rating.length; //Users' length
		double factor = 0, x = 0, y = 0;
		
		for (int u = 0; u < len; u++) {
			if(rating[u][item_i] > 0 && rating[u][item_j] > 0) {
				double avg_rating_u = getUserAvgRating(rating[u]);
				factor += (rating[u][item_i] - avg_rating_u) * (rating[u][item_j] - avg_rating_u);
				x += Math.pow(rating[u][item_i] - avg_rating_u, 2);
				y += Math.pow(rating[u][item_j] - avg_rating_u, 2);
			}
		}
		
		return factor / Math.sqrt(x * y);//similarity
	}
	
	
	/*
	 * getUserAvgRating:
	 * 
	 * Get average rating given by a user. 
	 * 
	 * - Input: all ratings given by u
	 * 
	 * - Output: average rating given by u
	 * 
	 */
	public double getUserAvgRating(int[] u){
		
		int sum = 0;
		
		for (int i = 0; i < u.length; i++ ) 
			sum += u[i];
		
		return (double)sum/u.length;
		
	}
	
	
	
	/*
	 * Step 2. Weighted sum - prediction
	 * 
	 * - Input:
	 * User u, item i
	 * 
	 * - Output:
	 * Predicted score of item i for user u
	 * 
	 */
	
	public double getPrediction(int u, int item_i) {
		Queue<SimilarityItem> similarItems_i = getSimilarItems(item_i);
		double factor = 0, denominator = 0;
		
		while(similarItems_i.size() > 0) {
			SimilarityItem s = similarItems_i.poll();
			double similarity = s.getSimilarity();
			factor += similarity * rating[u][s.getY()];
			denominator += similarity;
		}
		
		return factor/denominator;
	}
	
	
	/*
	 * getSimilarItems:
	 * 
	 * Get a set of simliar items for item_i, using getAdjustedCosine
	 * 
	 * 
	 */
	public Queue<SimilarityItem> getSimilarItems(int item_i){
		
		Queue<SimilarityItem> maxK = new PriorityQueue<SimilarityItem>();
		
		//To do: rule of queue. 
		
		for(int j = 0; j < rating[0].length; j++ ) {
			if(j != item_i){
				double similarity = getAdjustedCosine(item_i, j);
				SimilarityItem s = new SimilarityItem(item_i, j, similarity);
				maxK.offer(s);
				if(maxK.size() > K) {
					maxK.poll();
				}
			}
		}
		return maxK;
	}
	
	
	public static void main(String[] args) {
		/*
		 * 1. Read data from target dataset.
		 * 2. Transfer the data into int[][] rating. x is user, y is item, rating[x][y]: rates given by user x for item y.
		 * 3. Compute relationship between items in advance.
		 * 4. Every time, when we want to recommend items for user u. We calculate prediction for user u - all items which are not chosen before
		 * 5. Rank from high to low, do recommendation
		 * 
		 */
				
	}
	
	
	
	
}
