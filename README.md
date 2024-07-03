<!-- dx-header -->

# phoenix (DNAnexus Platform App)

## What does this app do?

Phoenix is a program designed for the automation of ClinVar annotation resource updates.

It consists of the two main python modules annotation_update.py and vep_config_update.py, used to set off the ClinVar annotation resource update and VEP config file updates respectively.
The nextflow script main.nf is used to orchestrate the annotation resource updates.
The nextflow script calls the python module clinvar_annotation_update.py, which carries out the b38 clinvar annotation resource update.

To run Phoenix, a valid DNAnexus file path must be provided to a config file in json format as described below.

Config file structure:
{
    "CLINVAR_BASE_LINK": "https://ftp.ncbi.nlm.nih.gov",
    "CLINVAR_LINK_PATH_B38": "/pub/clinvar/vcf_GRCh38/weekly/"
}

To build Phoenix as a nextflow applet run the following from the phoenix repo directory:
dx build --nextflow .

To set off the nextflow DNAnexus applet, run the following command, replacing the project ID you are using to run Phoenix in and the DNAnexus file path with the location of the config file you wish to use on DNAnexus.
dx run phoenix -i nextflow_pipeline_params="--config_path="dx://project-xxxx:/path/to/phoenix_config.json"" \
--destination="path/to/destination"

During early development, Phoenix can be run as an applet. However, it can easily be converted to a DNANexus app from an applet with the following command:
dx build --app --from applet-xxxx


## What data are required for this app to run?

**Packages**
* Python packages (specified in requirements.txt)

**Inputs**
Required
* `nextflow_pipeline_params`: --config_path="dx://project-xxxx:/path_to_config/phoenix_config.json"

Optional
* None

## What does this app output?

This app does not have an output


