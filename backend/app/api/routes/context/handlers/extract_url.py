"""Handler: Extract content from URL (webpage or PDF)"""
import logging
import re
import io
from typing import Dict, Any
from fastapi import HTTPException
import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Remove null characters and control characters that break PostgreSQL."""
    # Remove null characters
    text = text.replace('\u0000', '')
    text = text.replace('\x00', '')
    # Remove other control characters (except newline, tab, carriage return)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Clean multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

async def handle_extract_url(url: str) -> Dict[str, Any]:
    """Extract content from URL (supports webpages and PDFs)."""
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(400, "URL must start with http:// or https://")

        # Fetch URL with headers
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; OmegaBot/1.0)"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
        except httpx.TimeoutException:
            raise HTTPException(408, "La URL tardó demasiado en responder")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(404, "Página no encontrada")
            raise HTTPException(e.response.status_code, f"Error HTTP: {e.response.status_code}")
        except Exception as e:
            raise HTTPException(502, f"Error conectando a la URL: {str(e)}")

        # Detect content type
        content_type = response.headers.get('content-type', '').lower()
        url_lower = url.lower()
        is_pdf = url_lower.endswith('.pdf') or 'application/pdf' in content_type

        if is_pdf:
            # Extract PDF content
            try:
                pdf = PdfReader(io.BytesIO(response.content))
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"

                # Clean text (remove null chars, control chars, multiple newlines)
                text = clean_text(text)
                text = text[:50000]  # Limit to 50K chars

                # Extract title from filename
                title = url.split("/")[-1].replace(".pdf", "").replace("-", " ").replace("_", " ")

                if not text or len(text) < 50:
                    raise HTTPException(422, "No se pudo extraer texto del PDF")

                return {
                    "title": title,
                    "content": text,
                    "url": url,
                    "type": "pdf",
                    "char_count": len(text)
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"PDF extraction error: {e}")
                raise HTTPException(422, f"Error extrayendo PDF: {str(e)}")

        else:
            # Extract webpage content
            try:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract title
                title_tag = soup.find('title')
                title = title_tag.text.strip() if title_tag else url

                # Remove unwanted tags
                for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
                    tag.decompose()

                # Extract clean text
                text = soup.get_text(separator='\n', strip=True)

                # Clean text (remove null chars, control chars, multiple newlines)
                text = clean_text(text)
                text = text[:50000]  # Limit to 50K chars

                if not text or len(text) < 20:
                    raise HTTPException(422, "No se pudo extraer texto de la página")

                return {
                    "title": title,
                    "content": text,
                    "url": url,
                    "type": "webpage",
                    "char_count": len(text)
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Webpage extraction error: {e}")
                raise HTTPException(422, f"Error extrayendo página: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL extraction error: {e}")
        raise HTTPException(500, f"Error procesando URL: {str(e)}")
