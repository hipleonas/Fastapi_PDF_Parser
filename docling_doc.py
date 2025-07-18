#Convert a single pdf document 
"""
Demo PDF Link: https://arxiv.org/pdf/2402.16110
"""
from docling.document_converter import DocumentConverter

avix_source = "https://arxiv.org/pdf/2402.16110"
converter = DocumentConverter()
res = converter.convert(avix_source)
#using prefetch model

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import EasyOcrOptions, PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

artifacts = "/home/hiepquoc/Fastapi_PDF_Parser/artifacts/models"
pipline = PdfPipelineOptions(
    input_format = InputFormat.PDF,
    output_format = InputFormat.DOCUMENT,
    artifacts_path = artifacts,
)
doc_converter = DocumentConverter(
    pipeline_options = pipline,
    ocr_options = EasyOcrOptions(
        language = "eng",
        use_gpu = True,
    ),
)
"""
The main purpose of docling is to run local models
which are not sharing any user data with the remote service
Anyhow, there are valid use cases for using remote services
 for example invoking OCR engines from cloud vendors or the usage of hosted LLMs.

"""
if __name__ == "__main__":
    # Print the document in markdown format
    print(res.document.export_to_markdown())  

