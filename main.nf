nextflow.enable.dsl=2

pathToBin = "nextflow-bin"
pathToInput = "input"
pathToProjectDir = ""

process clinvarAnnotationUpdate
{
    script:
        
        """
        python3 ${pathToBin}/annotation_update.py
        """
}

workflow 
{
    // run phoenix clinvar annotation update
    clinvarAnnotationUpdate()
}
