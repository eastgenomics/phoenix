nextflow.enable.dsl=2

pathToBin = "nextflow-bin"
pathToInput = "input"
pathToProjectDir = ""

process clinvarAnnotationUpdate
{
    script:
        
        """
        python3 ${pathToBin}/clinvar_annotation_update.py ${params.config_path}
        """
}

workflow 
{
    // run phoenix clinvar annotation update
    clinvarAnnotationUpdate()
}
