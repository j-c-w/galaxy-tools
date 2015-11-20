#!/bin/bash -e
#
# List of dependencies
TOOL_DEPENDENCIES="rnachipintegrator/0.5.0-alpha.3
 xlwt/0.7.5
 xlrd/0.9.3
 xlutils/1.7.1"
# Where to find them
TOOL_DEPENDENCIES_DIR=$(pwd)/test.tool_dependencies.rnachipintegrator
if [ ! -d $TOOL_DEPENDENCIES_DIR ] ; then
    echo WARNING $TOOL_DEPENDENCIES_DIR not found >&2
    echo Creating tool dependencies dir
    mkdir -p $TOOL_DEPENDENCIES_DIR
    echo Installing tool dependencies
    $(dirname $0)/install_tool_deps.sh $TOOL_DEPENDENCIES_DIR
fi
# Load dependencies
for dep in $TOOL_DEPENDENCIES ; do
    env_file=$TOOL_DEPENDENCIES_DIR/$dep/env.sh
    if [ -e $env_file ] ; then
	. $env_file
    else
	echo ERROR no env.sh file found for $dep >&2
	exit 1
    fi
done
#
# rnachipintegrator_canonical_genes
#
# Test #1
RnaChipIntegrator --name=mm9 \
		  --cutoff=50000 \
		  --xls \
		  --compact \
		  test-data/mm9_canonical_genes.tsv test-data/mm9_summits.txt
mv mm9_peaks_per_feature.txt test-data/mm9_summits_per_feature.out
mv mm9_features_per_peak.txt test-data/mm9_features_per_summit.out
mv mm9.xls test-data/mm9_summits.xls
#
# Test #2
RnaChipIntegrator --name=mm9 \
		  --cutoff=50000 \
		  --xls \
		  --compact \
		  test-data/mm9_canonical_genes.tsv test-data/mm9_peaks.txt
mv mm9_peaks_per_feature.txt test-data/mm9_peaks_per_feature1.out
mv mm9_features_per_peak.txt test-data/mm9_features_per_peak1.out
mv mm9.xls test-data/mm9_peaks1.xls
#
# Test #3
RnaChipIntegrator --name=mm9 \
		  --cutoff=50000 \
		  --feature=gene \
		  --xls \
		  --compact \
		  test-data/mm9_canonical_genes.tsv test-data/mm9_peaks.txt
mv mm9_peaks_per_feature.txt test-data/mm9_peaks_per_feature2.out
mv mm9_features_per_peak.txt test-data/mm9_features_per_peak2.out
mv mm9.xls test-data/mm9_peaks2.xls
#
# Test #4
RnaChipIntegrator --name=mm9 \
		  --cutoff=50000 \
		  --xls \
		  --summary \
		  --pad \
		  test-data/mm9_canonical_genes.tsv test-data/mm9_peaks.txt
mv mm9_peaks_per_feature.txt test-data/mm9_peaks_per_feature3.out
mv mm9_features_per_peak.txt test-data/mm9_features_per_peak3.out
mv mm9_peaks_per_feature_summary.txt test-data/mm9_peaks_per_feature3.summary
mv mm9_features_per_peak_summary.txt test-data/mm9_features_per_peak3.summary
mv mm9.xls test-data/mm9_peaks3.xls
#
# rnachipintegrator_wrapper
#
# Test #1
RnaChipIntegrator --name=test \
		  --cutoff=130000 \
		  --promoter_region=-10000,2500 \
		  --xls \
		  --compact \
		  test-data/features.txt test-data/summits.txt
mv test_peaks_per_feature.txt test-data/summits_per_feature.out
mv test_features_per_peak.txt test-data/features_per_summit.out
mv test.xls test-data/summits.xls
#
# Test #2
RnaChipIntegrator --name=test \
		  --cutoff=130000 \
		  --promoter_region=-10000,2500 \
		  --xls \
		  --compact \
		  test-data/features.txt test-data/peaks.txt
mv test_peaks_per_feature.txt test-data/peaks_per_feature1.out
mv test_features_per_peak.txt test-data/features_per_peak1.out
mv test.xls test-data/peaks1.xls
#
# Test #3
RnaChipIntegrator --name=test \
		  --cutoff=130000 \
		  --xls \
		  test-data/features.txt test-data/peaks.txt
mv test_peaks_per_feature.txt test-data/peaks_per_feature2.out
mv test_features_per_peak.txt test-data/features_per_peak2.out
mv test.xls test-data/peaks2.xls
#
# Test #4
RnaChipIntegrator --name=test \
		  --cutoff=130000 \
		  --only-DE \
		  --feature=gene \
		  --xls \
		  --compact \
		  test-data/features.txt test-data/peaks.txt
mv test_peaks_per_feature.txt test-data/peaks_per_feature3.out
mv test_features_per_peak.txt test-data/features_per_peak3.out
mv test.xls test-data/peaks3.xls
#
# Test #5
RnaChipIntegrator --name=test \
		  --cutoff=130000 \
		  --xls \
		  --summary \
		  --pad \
		  test-data/features.txt test-data/peaks.txt
mv test_peaks_per_feature.txt test-data/peaks_per_feature4.out
mv test_features_per_peak.txt test-data/features_per_peak4.out
mv test_peaks_per_feature_summary.txt test-data/peaks_per_feature4.summary
mv test_features_per_peak_summary.txt test-data/features_per_peak4.summary
mv test.xls test-data/peaks4.xls
##
#