package test;

import java.io.FileWriter;
import java.io.IOException;
import java.util.Observable;
import java.util.Observer;

public class Logger implements Observer {

	private static Logger instance;
	public static String filePath;

	private Logger(String filePath, ObservableCacheSearcher ocs) {
		ocs.addObserver(this);
		Logger.filePath = filePath;
		try {
			new FileWriter(filePath, false).close(); // clear the file
		} catch (IOException e) {
		}
	}

	public static Logger getInstance(String fileName, ObservableCacheSearcher ocs) {
		// double check locking and lazy initialization 
		if (instance == null) {
			synchronized (Logger.class) {
				if (instance == null)
					instance = new Logger(fileName, ocs);
			}
		}
		return instance;
	}

	@Override
	public void update(Observable o, Object arg) {
		FileWriter fw;
		try {
			fw = new FileWriter(filePath, true);
			fw.write((String) arg + " " + ((CacheSearcher) o).getCachedResults().size() + "\n");
			fw.close();
		} catch (IOException e) {
		}
	}

}
