package test;

import java.util.Observable;
import java.util.Set;

public class ObservableCacheSearcher extends Observable implements CacheSearcher {
	
	CacheSearcher cs;
	Set<Result> s;

	public ObservableCacheSearcher(CacheSearcher cs) {
		this.cs = cs;
		s = cs.getCachedResults();
	}

	@Override
	public Result search(String text, String rootPath) {
		Result r = cs.search(text, rootPath);
		Set<Result> hs = cs.getCachedResults();
		String retStr = "";
		String semic = "";
		for (Result rr : hs) {
			if (!s.contains(rr)) { // something was added
				retStr = rr.getQuery() + " added";
				semic = ";";
			}
		}
		for (Result rr : s) {
			if (!hs.contains(rr)) // something was removed
				retStr = rr.getQuery() + " removed" + semic + retStr;
		}
		s = hs;
		setChanged(); // should it be in the "if"
		if (!retStr.equals("")) // if there was a change
			notifyObservers(retStr);
		return r;
	}

	@Override
	public Set<Result> getCachedResults() {
		return cs.getCachedResults();
	}

	@Override
	public void clear() {
		cs.clear();
		s.clear();
		setChanged();
		notifyObservers("cleared");
	}

	@Override
	public void remove(Result r) {
		cs.remove(r);
		s.remove(r);
		setChanged();
		notifyObservers(r.getQuery() + " removed");
	}

}
