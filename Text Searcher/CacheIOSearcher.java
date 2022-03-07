package test;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

public class CacheIOSearcher implements CacheSearcher {

	IOSearcher ios;
	HashMap<String, Result> m;

	public CacheIOSearcher() {
		ios = new IOSearcher();
		m = new HashMap<String, Result>();
	}

	@Override
	public Result search(String text, String rootPath) {
		// String key = text + "-" + rootPath; // the key is the searched string + the
		// root path
		if (!m.isEmpty() && m.containsKey(text)) // the key is the searched string because the root path is constant
			return m.get(text);
		Result r = ios.search(text, rootPath);
		m.put(text, r);
		return r;
	}

	@Override
	public Set<Result> getCachedResults() {
		return new HashSet<Result>(m.values());
	}

	@Override
	public void clear() {
		m.clear();
	}

	@Override
	public void remove(Result r) {
		for (String key : m.keySet()) {
			if (m.get(key).getQuery().equals(r.getQuery())) {
				m.remove(key);
				return;
			}
		}
	}

}
