package test;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class IOSearcher implements TextSearcher {

	@Override
	public Result search(String text, String rootPath) {
		Map<String, Set<String>> m = new HashMap<String, Set<String>>();
		File dir = new File(rootPath);
		File[] files = dir.listFiles();
		if (files != null) { // there are files/directories in the directory
			for (File file : files) {
				if (file.isDirectory())
					m.putAll(search(text, file.getPath()).getAnswer());
				else if (file.getAbsolutePath().endsWith(".txt")) {
					Set<String> s = searchLines(text, file);
					if (!s.isEmpty())
						m.put(file.getAbsolutePath(), s);
				}
			}
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

	public Set<String> searchLines(String text, File f) {
		Set<String> s = new HashSet<String>();
		try {
			Files.lines(f.toPath(), StandardCharsets.ISO_8859_1).filter(str -> str.contains(text))
					.forEach(str -> s.add(str));
		} catch (IOException e) {
		}
		return s;
	}

}
