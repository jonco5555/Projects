package test;

import java.util.HashMap;
import java.util.Set;

public class LFUCacheSearcher implements CacheSearcher {

	CacheSearcher cs;
	int max;
	HashMap<Result, Used> m;

	public LFUCacheSearcher(CacheSearcher cs, int max) {
		this.cs = cs;
		this.max = max;
		m = new HashMap<Result, Used>();
	}

	@Override
	public Result search(String text, String rootPath) {
		Result r = cs.search(text, rootPath);
		if (!m.isEmpty() && m.containsKey(r))
			m.put(r, new Used(m.get(r).count + 1)); // if the same search again, it will override the previous one with
													// an updated timestamp and +1 counter
		else
			m.put(r, new Used()); // with count=0
		if (cs.getCachedResults().size() == max) {
			long minTime = System.nanoTime();
			int minCount = Integer.MAX_VALUE;
			Result toRmv = null;
			for (Result rr : m.keySet()) {
				if (rr != r) { // I don't want to remove the one I've just searched.
								// Otherwise, if for all results in cache the count is > 1, then the cache won't
								// change and all new results will be removed immediately
					if (m.get(rr).count < minCount) { // remove LFU
						minCount = m.get(rr).count;
						minTime = m.get(rr).time;
						toRmv = rr;
					} else if (m.get(rr).count == minCount && m.get(rr).time < minTime) { // remove LRU
						minCount = m.get(rr).count;
						minTime = m.get(rr).time;
						toRmv = rr;
					}
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

	public class Used {

		long time;
		int count;

		public Used() { // if map doesn't contain the result
			time = System.nanoTime();
			count = 1;
		}

		public Used(int count) { // if map contains the result
			time = System.nanoTime();
			this.count = count;
		}

	}
}
