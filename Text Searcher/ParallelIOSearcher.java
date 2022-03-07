package test;

import java.io.File;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveTask;

public class ParallelIOSearcher extends IOSearcher {

	ForkJoinPool fjp;

	public class RecSearcher extends RecursiveTask<Result> {

		private static final long serialVersionUID = 1L;
		private String text;
		private String path;

		public RecSearcher(String text, String path) {
			this.text = text;
			this.path = path;
		}

		@Override
		protected Result compute() {
			Map<String, Set<String>> m = new HashMap<String, Set<String>>();
			LinkedList<RecSearcher> l = new LinkedList<RecSearcher>();
			File dir = new File(path);
			File[] files = dir.listFiles();
			if (files != null) { // there are files/directories in the directory
				for (File file : files) {
					if (file.isDirectory()) {
						l.add(new RecSearcher(this.text, file.getAbsolutePath()));
						l.getLast().fork();
					} else if (file.getAbsolutePath().endsWith(".txt")) {
						Set<String> s = searchLines(text, file);
						if (!s.isEmpty())
							m.put(file.getAbsolutePath(), s);
					}
				}
				for (RecSearcher rs : l)
					m.putAll(rs.join().getAnswer());
			}

			return new Result() {

				@Override
				public String getQuery() {
					return text;
				}

				@Override
				public Map<String, Set<String>> getAnswer() {
					return m;
				}
			};
		}

	}

	@Override
	public Result search(String text, String rootPath) {
		this.fjp = new ForkJoinPool();
		Result r = this.fjp.invoke(new RecSearcher(text, rootPath)); // invoke waits, submit gives Future
		this.fjp.shutdown();
		return r;
	}
}
