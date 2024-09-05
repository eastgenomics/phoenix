nextflow.enable.dsl=2

pathToBin = "nextflow-bin"
pathToInput = "input"
pathToProjectDir = ""

process clinvarAnnotationUpdate
{
    input:
        path config_path
        path credentials_path

    script:
        
        """
        python3 ${pathToBin}/clinvar_annotation_update.py \
        --config_file ${config_path} --credentials_file ${credentials_path}
        """
}

workflow 
{
    // run phoenix clinvar annotation update
    clinvarAnnotationUpdate(params.config_path, params.credentials_path)
}
