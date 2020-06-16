OK, so I've added a shell.nix.

Steps are:

1. Get into the nix-shell
2. Go to tools/motif_tools/
3. Run:
	perl -d:NYTProf TFBScluster_candidates.pl test-data/SARSCoV2_veryshort.fa 2 30 20 1 include outputtest
4. Run nytprofhtml nytprof.out
5. Go into the output folder and there is an 'index.html' file that contains the profiling results
