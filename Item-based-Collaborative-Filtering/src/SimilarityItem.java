public class SimilarityItem{
	private int x;
	private int y;
	private double similarity;
	
	public double getSimilarity(){
		return similarity;
	}
	
	public int getX() {
		return x;
	}
	
	public int getY() {
		return y;
	}
	
	public SimilarityItem(int _x, int _y, double _similarity) {
		x = _x;
		y = _y;
		similarity = _similarity;
	}
}
