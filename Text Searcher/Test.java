package test;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;

public class Test {

	public static void main(String[] args) {
		// 1
		System.out.println("----- 1 -----");
		IOSearcher ios = new IOSearcher();
		Result r1 = ios.search("can you", "search_folder"); // to compare to other searchers
		if (ios.search("see the Mock Turtle", "search_folder").getAnswer().size() != 1)
			System.out.println("Search doesn't work");
		else
			System.out.println("Search works");
		if (ios.search("\"Where's your gom jabbar?", "search_folder").getAnswer().size() != 1)
			System.out.println("Search doesn't work");
		else
			System.out.println("Search works");

		// 2
		System.out.println("\n----- 2 -----");
		ParallelIOSearcher pios = new ParallelIOSearcher();
		Result r2 = pios.search("can you", "search_folder");
		if (!r2.getAnswer().equals(r1.getAnswer()))
			System.out.println("Search doesn't work");
		else
			System.out.println("Search works");
		if (pios.fjp.getStealCount() <= 1)
			System.out.println("Threads weren't used correctly");
		else
			System.out.println("Threads were used correctly");

		// 3
		System.out.println("\n----- 3 -----");
		CacheIOSearcher cios = new CacheIOSearcher();
		long t0 = System.nanoTime();
		Result r3 = cios.search("can you", "search_folder");
		long delta0 = System.nanoTime() - t0;
		if (!r3.getAnswer().equals(r1.getAnswer()))
			System.out.println("Search doesn't work");
		else
			System.out.println("Search works");

		t0 = System.nanoTime();
		r3 = cios.search("can you", "search_folder");
		long delta1 = System.nanoTime() - t0;
		if (delta1 > delta0) // it is the same search again so should return immediately
			System.out.println("Cache implementation doesn't work");
		else
			System.out.println("Cache implementation works");

		r3 = cios.search("Can you", "search_folder");
		if (cios.getCachedResults().size() != 2)
			System.out.println("Results aren't saved");

		cios.remove(r3);
		if (cios.getCachedResults().size() != 1)
			System.out.println("Remove doesn't work correctly");

		cios.clear();
		if (cios.getCachedResults().size() != 0)
			System.out.println("Clear doesn't work correctly");

		// 4
		System.out.println("\n----- 4 -----");
		LRUCacheSearcher lrucs = new LRUCacheSearcher(new CacheIOSearcher(), 3); // max size 3
		Result r4 = lrucs.search("can you", "search_folder");
		if (!r4.getAnswer().equals(r1.getAnswer()))
			System.out.println("Search doesn't work");
		else
			System.out.println("Search works");

		r4 = lrucs.search("Can you", "search_folder");
		lrucs.search("can you", "search_folder");
		lrucs.search("you cannot", "search_folder"); // now 'Can you' should be removed
		if (lrucs.getCachedResults().contains(r4))
			System.out.println("LRU doesn't work");
		else
			System.out.println("LRU works");

		// 5
		System.out.println("\n----- 5 -----");
		LFUCacheSearcher lfucs = new LFUCacheSearcher(new CacheIOSearcher(), 3); // max size 3
		Result r5 = lfucs.search("can you", "search_folder");
		if (!r5.getAnswer().equals(r1.getAnswer()))
			System.out.println("Search doesn't work");
		else
			System.out.println("Search works");

		lfucs.search("can you", "search_folder");
		Result r55 = lfucs.search("Can you", "search_folder");
		lfucs.search("you cannot", "search_folder"); // now 'Can you' should be removed
		if (lfucs.getCachedResults().contains(r55))
			System.out.println("LFU doesn't work");
		else
			System.out.println("LFU works");

		lfucs.search("you cannot", "search_folder");
		lfucs.search("You cannot", "search_folder"); // now 'can you' should be removed (lru)
		if (lfucs.getCachedResults().contains(r5))
			System.out.println("LRU in LFU doesn't work");
		else
			System.out.println("LRU in LFU works");

		// 6 + 7
		System.out.println("\n----- 6+7 -----");
		ObservableCacheSearcher ocs = new ObservableCacheSearcher(new LRUCacheSearcher(new CacheIOSearcher(), 3));
		Logger.getInstance("log.txt", ocs);

		Result r6 = ocs.search("can you", "search_folder");
		if (!r6.getAnswer().equals(r1.getAnswer()))
			System.out.println("Search doesn't work");
		else
			System.out.println("Search works");

		r6 = ocs.search("Can you", "search_folder");
		ocs.search("can you", "search_folder");
		ocs.search("you cannot", "search_folder"); // now 'Can you' should be removed
		if (ocs.getCachedResults().contains(r6))
			System.out.println("LRU decorator doesn't work");
		else
			System.out.println("LRU decorator works");

		// general check for any flow
		boolean[] b = { true };
		try {
			Files.lines(new File("log.txt").toPath())
					.filter(str -> !str.matches("(.+ removed(;.+ added \\d+)?)|(.+ added \\d+)"))
					.forEach(str -> b[0] = false);
			if (!b[0])
				System.out.println("General check doesn't look correct");
			else
				System.out.println("General check looks correct");
		} catch (IOException e) {
			e.printStackTrace();
		}

		// specific check for current flow
		boolean bb = true;
		try (BufferedReader br = new BufferedReader(new FileReader("log.txt"))) {
			if (!br.readLine().equals("can you added 1")) // first line
				bb = false;
			if (!br.readLine().equals("Can you added 2")) // second line
				bb = false;
			if (!br.readLine().equals("Can you removed;you cannot added 2")) // third line
				bb = false;
			if (br.readLine() != null) // there shouldn't be more lines
				bb = false;
			br.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
			bb = false;
		} catch (IOException e) {
			e.printStackTrace();
			bb = false;
		}
		if (!bb)
			System.out.println("Print to file doesn't work correctly");
		else
			System.out.println("Print to file works correctly");
	}
}
