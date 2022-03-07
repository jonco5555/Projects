package test;

import java.util.HashMap;
import java.util.Set;

public class LRUCacheSearcher implements CacheSearcher {

	CacheSearcher cs;
	int max;
	HashMap<Result, Long> m;

	public LRUCacheSearcher(CacheSearcher cs, int max) {
		this.cs = cs;
		this.max = max;
		m = new HashMap<Result, Long>();
	}

	@Override
	public Result search(String text, String rootPath) {
		Result r = cs.search(text, rootPath);
		m.put(r, System.nanoTime()); // if the same search again, it will override the previous one with an
												// updated timestamp
		if (cs.getCachedResults().size() == max) { // once we reach max I remove a Result immediately
			long min = System.nanoTime();
			Result toRmv = null;
			for (Result rr : m.keySet()) {
				if (m.get(rr) < min) {
					min = m.get(rr);
					toRmv = rr;
				}
			}
			m.remove(toRmv);
			cs.remove(toRmv);
		}
		return r;
	}

	@Override
	public Set<Result> getCachedResults() {
		return cs.getCachedResults();
	}

	@Override
	public void clear() {
		cs.clear();
		m.clear();
	}

	@Override
	public void remove(Result r) {
		cs.remove(r);
		m.remove(r);
	}
}
