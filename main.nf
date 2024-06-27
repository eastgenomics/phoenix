nextflow.enable.dsl=2

pathToBin = "nextflow-bin"
pathToInput = "input"
pathToProjectDir = ""

process clinvarAnnotationUpdate
{
    input:
        path config_path

    script:
        
        """
        python3 ${pathToBin}/clinvar_annotation_update.py ${config_path}
        """
}

workflow 
{
    // run phoenix clinvar annotation update
    clinvarAnnotationUpdate(params.config_path)
}
