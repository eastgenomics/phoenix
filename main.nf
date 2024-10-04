nextflow.enable.dsl=2

pathToBin = "nextflow-bin"
pathToInput = "input"
pathToProjectDir = ""

process clinvarAnnotationUpdate
{
    container 'dx://project-GkxxZq843Zq2f0Gk3Z40p7BJ:file-Gqzy3fj43Zq3Bz575J27Zj8Z'

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
