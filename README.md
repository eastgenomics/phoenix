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

To set off the nextflow DNAnexus applet, run the following command, replacing the applet ID you have generated and the DNAnexus file path with the location of the config file you wish to use on DNAnexus.
dx run applet-GkyY1Vj43Zq9Y5B6v1Q89XFg -i nextflow_pipeline_params="--config_path="dx://project-GkxxZq843Zq2f0Gk3Z40p7BJ:/Config/phoenix_config.json""

During early development, Phoenix can be run as an applet. However, it an easily be converted to a DNANexus app from an applet with the following command:
dx build --app --from applet-xxxx
