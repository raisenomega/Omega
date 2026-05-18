"""Handler: Extract text from uploaded file (PDF, TXT, MD)"""
import logging
import io
from typing import Dict, Any
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
from .extract_url import clean_text

logger = logging.getLogger(__name__)

async def handle_extract_file(file: UploadFile) -> Dict[str, Any]:
    """Extract text from uploaded file (PDF, TXT, MD)."""
    try:
        content_type = file.content_type or ""
        filename = file.filename or "unknown"

        # Read file content
        content = await file.read()

        # PDF extraction
        if "pdf" in content_type.lower() or filename.lower().endswith(".pdf"):
            try:
                pdf = PdfReader(io.BytesIO(content))
                text = ""
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"

                if not text.strip():
                    raise HTTPException(422, "No se pudo extraer texto del PDF")

                # Clean text (remove null chars, control chars)
                text = clean_text(text)
                text = text[:50000]  # Limit to 50K chars

                title = filename.replace(".pdf", "").replace(".PDF", "")

                return {
                    "title": title,
                    "content": text,
                    "type": "pdf",
                    "char_count": len(text)
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"PDF extraction error: {e}")
                raise HTTPException(500, f"Error procesando PDF: {str(e)}")

        # TXT / MD extraction
        elif filename.lower().endswith((".txt", ".md")):
            try:
                text = content.decode("utf-8", errors="ignore")
                text = clean_text(text)
                text = text[:50000]  # Limit to 50K chars

                # Extract title from filename
                title = filename.rsplit(".", 1)[0]
                file_type = "markdown" if filename.lower().endswith(".md") else "text"

                return {
                    "title": title,
                    "content": text,
                    "type": file_type,
                    "char_count": len(text)
                }
            except Exception as e:
                logger.error(f"Text file extraction error: {e}")
                raise HTTPException(500, f"Error procesando archivo de texto: {str(e)}")

        else:
            raise HTTPException(422, "Formato no soportado. Usa PDF, TXT o MD")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File extraction error: {e}")
        raise HTTPException(500, f"Error procesando archivo: {str(e)}")
