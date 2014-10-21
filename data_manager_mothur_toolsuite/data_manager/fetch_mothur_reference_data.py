#!/usr/bin/env python
#
# Fetch reference data for the Galaxy 'mothur_toolsuite'
import os
import optparse
import tempfile
import shutil
import urllib2
import zipfile
import tarfile

from galaxy.util.json import from_json_string, to_json_string

# When extracting files from archives, skip names that
# start with the following strings
IGNORE_PATHS = ('.','__MACOSX/')

# Map file extensions to data table names
MOTHUR_FILE_TYPES = { ".map": "map",
                      ".fasta": "aligndb",
                      ".pat": "lookup",
                      ".tax": "taxonomy" }

# Reference data URLs
MOTHUR_REFERENCE_DATA = {
    # Look up data
    # http://www.mothur.org/wiki/Lookup_files
    "lookup_titanium": {
        "GS FLX Titanium": ["http://www.mothur.org/w/images/9/96/LookUp_Titanium.zip",]
    },
    "lookup_gsflx": {
        "GSFLX": ["http://www.mothur.org/w/images/8/84/LookUp_GSFLX.zip",]
    },
    "lookup_gs20": {
        "GS20": ["http://www.mothur.org/w/images/7/7b/LookUp_GS20.zip",]
    },
    # RDP reference files
    # http://www.mothur.org/wiki/RDP_reference_files
    "RDP_v9": {
        "16S rRNA reference (RDP) (training set v9)":
        ["http://www.mothur.org/w/images/7/72/Trainset9_032012.rdp.zip",],
        "16S rRNA reference (PDS) (training set v9)":
        ["http://www.mothur.org/w/images/5/59/Trainset9_032012.pds.zip",],
    },
    "RDP_v7": {
        "16S rRNA reference (RDP) (training set v7)":
        ["http://www.mothur.org/w/images/2/29/Trainset7_112011.rdp.zip",],
        "16S rRNA reference (PDS) (training set v7)":
        ["http://www.mothur.org/w/images/4/4a/Trainset7_112011.pds.zip",],
        "8S rRNA reference (RDP) (Fungi, training set v7)":
        ["http://www.mothur.org/w/images/3/36/FungiLSU_train_v7.zip",],
    },
    "RDP_v6": {
        "RDP training set version 6":
        ["http://www.mothur.org/w/images/4/49/RDPTrainingSet.zip",],
    },
    # Silva reference files
    # http://www.mothur.org/wiki/Silva_reference_files
    "silva_release_119": {
        "SILVA bacterial, archaea and eukarya references (release 119)":
        ["http://www.mothur.org/w/images/2/27/Silva.nr_v119.tgz",],
        "SILVA recreated SEED database (release 119)":
        ["http://www.mothur.org/w/images/5/56/Silva.seed_v119.tgz",],
    },
    "silva_release_102": {
        "SILVA bacterial references (release 102)":
        ["http://www.mothur.org/w/images/9/98/Silva.bacteria.zip",],
        "SILVA archaeal references (release 102)":
        ["http://www.mothur.org/w/images/3/3c/Silva.archaea.zip",],
        "SILVA Eukaryotic references (release 102)":
        ["http://www.mothur.org/w/images/1/1a/Silva.eukarya.zip",],
    },
    "silva_gold_bacteria": {
        "SILVA-based alignment for chimera.slayer (gold.bacteria)":
        ["http://www.mothur.org/w/images/f/f1/Silva.gold.bacteria.zip",],
    },
    # Greengenes
    # http://www.mothur.org/wiki/Greengenes-formatted_databases
    "greengenes_August2013": {
        "Greengenes reference alignment (gg_13_8_99 August 2013 release)":
        ["http://www.mothur.org/w/images/1/19/Gg_13_8_99.refalign.tgz",],
        "Greengenes reference taxonomy (gg_13_8_99 August 2013 release)":
        ["http://www.mothur.org/w/images/6/68/Gg_13_8_99.taxonomy.tgz",],
    },
    "greengenes_May2013": {
        "Greengenes reference alignment (gg_13_5_99 May 2013 release)":
        ["http://www.mothur.org/w/images/c/cd/Gg_13_5_99.refalign.tgz",],
        "Greengenes reference taxonomy (gg_13_5_99 May 2013 release)":
        ["http://www.mothur.org/w/images/9/9d/Gg_13_5_99.taxonomy.tgz",],
    },
    "greengenes_old": {
        "Greengenes reference alignment (pre-May 2013)":
        ["http://www.mothur.org/w/images/7/72/Greengenes.alignment.zip",],
        "Greengenes reference taxonomy (pre-May 2013)":
        ["http://www.mothur.org/w/images/1/16/Greengenes.tax.tgz",],
    },
    "greengenes_gold_alignment": {
        "greengenes gold alignment":
        ["http://www.mothur.org/w/images/2/21/Greengenes.gold.alignment.zip",],
    },
    # Secondary structure maps
    # http://www.mothur.org/wiki/Secondary_structure_map
    "secondary_structure_maps_silva": {
        "SILVA secondary structure mapping files":
        ["http://www.mothur.org/w/images/6/6d/Silva_ss_map.zip",],
    },
    "secondary_structure_maps_greengenes": {
        "Greengenes secondary structure mapping files":
        ["http://www.mothur.org/w/images/4/4b/Gg_ss_map.zip",],
    },
    # Lane masks: not used here?
    "lane_masks": ["http://www.mothur.org/w/images/2/2a/Lane1241.gg.filter",
                   "http://www.mothur.org/w/images/a/a0/Lane1287.gg.filter",
                   "http://www.mothur.org/w/images/3/3d/Lane1349.gg.filter",
                   "http://www.mothur.org/w/images/6/6d/Lane1349.silva.filter",]
}

# Utility functions for interacting with Galaxy JSON

def read_input_json(jsonfile):
    """Read the JSON supplied from the data manager tool

    Returns a tuple (param_dict,extra_files_path)

    'param_dict' is an arbitrary dictionary of parameters
    input into the tool; 'extra_files_path' is the path
    to a directory where output files must be put for the
    receiving data manager to pick them up.

    NB the directory pointed to by 'extra_files_path'
    doesn't exist initially, it is the job of the script
    to create it if necessary.

    """
    params = from_json_string(open(jsonfile).read())
    return (params['param_dict'],
            params['output_data'][0]['extra_files_path'])

# Utility functions for creating data table dictionaries
#
# Example usage:
# >>> d = create_data_tables_dict()
# >>> add_data_table(d,'my_data')
# >>> add_data_table_entry(dict(dbkey='hg19',value='human'))
# >>> add_data_table_entry(dict(dbkey='mm9',value='mouse'))
# >>> print str(to_json_string(d))

def create_data_tables_dict():
    """Return a dictionary for storing data table information

    Returns a dictionary that can be used with 'add_data_table'
    and 'add_data_table_entry' to store information about a
    data table. It can be converted to JSON to be sent back to
    the data manager.

    """
    d = {}
    d['data_tables'] = {}
    return d

def add_data_table(d,table):
    """Add a data table to the data tables dictionary

    Creates a placeholder for a data table called 'table'.

    """
    d['data_tables'][table] = []

def add_data_table_entry(d,table,entry):
    """Add an entry to a data table

    Appends an entry to the data table 'table'. 'entry'
    should be a dictionary where the keys are the names of
    columns in the data table.

    """
    d['data_tables'][table].append(entry)

# Utility functions for downloading and unpacking archive files

def download_file(url,target=None,wd=None):
    """Download a file from a URL

    Fetches a file from the specified URL.

    If 'target' is specified then the file is saved to this
    name; otherwise it's saved as the basename of the URL.

    If 'wd' is specified then it is used as the 'working
    directory' where the file will be save on the local
    system.

    Returns the name that the file is saved with.

    """
    print "Downloading %s" % url
    if not target:
        target = os.path.basename(url)
    if wd:
        target = os.path.join(wd,target)
    print "Saving to %s" % target
    open(target,'wb').write(urllib2.urlopen(url).read())
    return target

def unpack_zip_archive(filen,wd=None):
    """Extract files from a ZIP archive

    Given a ZIP archive, extract the files it contains
    and return a list of the resulting file names and 
    paths.

    'wd' specifies the working directory to extract
    the files to, otherwise they are extracted to the
    current working directory.

    Once all the files are extracted the ZIP archive
    file is deleted from the file system.

    """
    if not zipfile.is_zipfile(filen):
        print "%s: not ZIP formatted file"
        return [filen]
    file_list = []
    z = zipfile.ZipFile(filen)
    for name in z.namelist():
        if reduce(lambda x,y: x or name.startswith(y),IGNORE_PATHS,False):
            print "Ignoring %s" % name
            continue
        if wd:
            target = os.path.join(wd,name)
        else:
            target = name
        if name.endswith('/'):
            # Make directory
            print "Creating dir %s" % target
            try:
                os.makedirs(target)
            except OSError:
                pass
        else:
            # Extract file
            print "Extracting %s" % name
            try:
                os.makedirs(os.path.dirname(target))
            except OSError:
                pass
            open(target,'wb').write(z.read(name))
            file_list.append(target)
    print "Removing %s" % filen
    os.remove(filen)
    return file_list

def unpack_tar_archive(filen,wd=None):
    """Extract files from a TAR archive

    Given a TAR archive (which optionally can be
    compressed with either gzip or bz2), extract the
    files it contains and return a list of the
    resulting file names and paths.

    'wd' specifies the working directory to extract
    the files to, otherwise they are extracted to the
    current working directory.

    Once all the files are extracted the ZIP archive
    file is deleted from the file system.

    """
    file_list = []
    if wd:
        path = wd
    else:
        path = '.'
    if not tarfile.is_tarfile(filen):
        print "%s: not TAR file"
        return [filen]
    t = tarfile.open(filen)
    for name in t.getnames():
        # Extract file
        print "Extracting %s" % name
        t.extract(name,wd)
        if wd:
            target = os.path.join(wd,name)
        else:
            target = name
        file_list.append(target)
    print "Removing %s" % filen
    os.remove(filen)
    return file_list

def unpack_archive(filen,wd=None):
    """Extract files from an archive

    Wrapper function that calls the appropriate
    unpacking function depending on the archive
    type, and returns a list of files that have
    been extracted.

    'wd' specifies the working directory to extract
    the files to, otherwise they are extracted to the
    current working directory.

    """
    print "Unpack %s" % filen
    ext = os.path.splitext(filen)[1]
    print "Extension: %s" % ext
    if ext == ".zip":
        return unpack_zip_archive(filen,wd=wd)
    elif ext == ".tgz":
        return unpack_tar_archive(filen,wd=wd)
    else:
        return [filen]

def fetch_files(urls,wd=None,files=None):
    """Download and unpack files from a list of URLs

    Given a list of URLs, download and unpack each
    one, and return a list of the extracted files.

    'wd' specifies the working directory to extract
    the files to, otherwise they are extracted to the
    current working directory.

    If 'files' is given then the list of extracted
    files will be appended to this list before being
    returned.

    """
    if files is None:
        files = []
    for url in urls:
        filen = download_file(url,wd=wd)
        files.extend(unpack_archive(filen,wd=wd))
    return files

# Utility functions specific to the Mothur reference data

def identify_type(filen):
    """Return the data table name based on the file name

    """
    ext = os.path.splitext(filen)[1]
    try:
        return MOTHUR_FILE_TYPES[ext]
    except KeyError:
        return None

def get_name(filen):
    """Generate a descriptive name based on the file name
    """
    type_ = identify_type(filen)
    name = os.path.splitext(os.path.basename(filen))[0]
    for delim in ('.','_'):
        name = name.replace(delim,' ')
    return name

if __name__ == "__main__":
    print "Starting..."

    # Read command line
    parser = optparse.OptionParser()
    options,args = parser.parse_args()
    print "options: %s" % options
    print "args   : %s" % args
    if len(args) != 2:
        p.error("Need to supply JSON file name and a dataset name")
    jsonfile = args[0]
    datasets = args[1].split(',')

    # Read the input JSON
    param_dict,target_dir = read_input_json(jsonfile)

    # Make the target directory
    print "Making %s" % target_dir
    os.mkdir(target_dir)

    # Set up data tables dictionary
    data_tables = create_data_tables_dict()
    add_data_table(data_tables,'mothur_lookup')
    add_data_table(data_tables,'mothur_aligndb')
    add_data_table(data_tables,'mothur_map')
    add_data_table(data_tables,'mothur_taxonomy')

    # Make working dir
    wd = tempfile.mkdtemp(suffix=".mothur",dir=os.getcwd())
    print "Working dir %s" % wd
    # Iterate over all requested reference data URLs
    for dataset in datasets:
        print "Handling dataset '%s'" % dataset
        for name in MOTHUR_REFERENCE_DATA[dataset]:
            for f in fetch_files(MOTHUR_REFERENCE_DATA[dataset][name],wd=wd):
                type_ = identify_type(f)
                print "%s\t\'%s'\t.../%s" % (type_,
                                             name,
                                             os.path.basename(f))
                if type_ is not None:
                    # Move to target dir
                    ref_data_file = os.path.basename(f)
                    f1 = os.path.join(target_dir,ref_data_file)
                    print "Moving %s to %s" % (f,f1)
                    os.rename(f,f1)
                    # Add entry to data table
                    table_name = "mothur_%s" % type_
                    add_data_table_entry(data_tables,table_name,dict(name=name,
                                                                     value=ref_data_file))
    # Remove working dir
    print "Removing %s" % wd
    shutil.rmtree(wd)
    # Write output JSON
    print "Outputting JSON"
    print str(to_json_string(data_tables))
    open(jsonfile,'wb').write(to_json_string(data_tables))
    print "Done."
