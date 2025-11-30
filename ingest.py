"""
Document ingestion module for processing PDFs and building knowledge base with ChromaDB.
"""

import os
import PyPDF2
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import hashlib
from db import Database


class DocumentIngester:
    """Handles PDF document ingestion and ChromaDB knowledge base creation."""
    
    def __init__(self, chroma_db_path: str = "./chroma_db", 
                 collection_name: str = "onboarding_docs"):
        """Initialize ChromaDB client and collection."""
        self.chroma_db_path = chroma_db_path
        self.collection_name = collection_name
        self.db = Database()
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Use default embedding function (sentence-transformers)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[List[Dict[str, str]], Optional[str]]:
        """Extract text from PDF file, splitting by pages.
        
        Returns:
            Tuple of (chunks list, error_message if any)
        """
        chunks = []
        error_msg = None
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    return [], "PDF file is password-protected. Please remove the password and try again."
                
                # Check number of pages
                num_pages = len(pdf_reader.pages)
                if num_pages == 0:
                    return [], "PDF file appears to be empty or corrupted."
                
                total_text_length = 0
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text.strip():
                            chunks.append({
                                'text': text,
                                'page': page_num + 1,
                                'source': os.path.basename(pdf_path)
                            })
                            total_text_length += len(text.strip())
                    except Exception as page_error:
                        # Continue with other pages if one page fails
                        print(f"Warning: Could not extract text from page {page_num + 1}: {page_error}")
                
                # Check if we extracted any text
                if not chunks:
                    if num_pages > 0:
                        return [], "No extractable text found in PDF. This might be a scanned document (image-based PDF). Please use OCR to extract text first."
                    else:
                        return [], "Could not extract any text from the PDF file."
                        
        except PyPDF2.errors.PdfReadError as e:
            return [], f"PDF file is corrupted or invalid: {str(e)}"
        except FileNotFoundError:
            return [], f"PDF file not found: {pdf_path}"
        except PermissionError:
            return [], f"Permission denied: Cannot read PDF file {pdf_path}"
        except Exception as e:
            error_msg = f"Unexpected error extracting text from PDF: {str(e)}"
            print(error_msg)
            return [], error_msg
        
        return chunks, None
    
    def chunk_text(self, text: str, chunk_size: int = 1000, 
                   overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks
    
    def process_pdf(self, pdf_path: str, metadata: Dict = None) -> Tuple[bool, Optional[str]]:
        """Process a PDF file and add to ChromaDB.
        
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        try:
            # Extract text from PDF
            pdf_chunks, extract_error = self.extract_text_from_pdf(pdf_path)
            
            if extract_error:
                return False, extract_error
            
            if not pdf_chunks:
                return False, "No text could be extracted from the PDF file. The file might be empty, corrupted, or image-based (scanned document)."
            
            # Prepare documents for ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            filename = os.path.basename(pdf_path)
            try:
                doc_id = self.db.add_document(filename, pdf_path, 'pdf')
            except PermissionError as db_error:
                return False, f"Database error: {str(db_error)}. The database file may be read-only or you may not have write permissions."
            
            for chunk_data in pdf_chunks:
                # Further chunk if needed
                text_chunks = self.chunk_text(chunk_data['text'])
                
                for idx, chunk_text in enumerate(text_chunks):
                    chunk_id = f"{filename}_{chunk_data['page']}_{idx}"
                    chunk_hash = hashlib.md5(chunk_id.encode()).hexdigest()
                    
                    documents.append(chunk_text)
                    chunk_metadata = {
                        'source': chunk_data['source'],
                        'page': chunk_data['page'],
                        'chunk_index': idx,
                        'doc_id': doc_id
                    }
                    if metadata:
                        chunk_metadata.update(metadata)
                    metadatas.append(chunk_metadata)
                    ids.append(chunk_hash)
            
            # Add to ChromaDB collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            # Update document status
            self.db.update_document_status(doc_id, 'processed')
            
            return True, None
            
        except PermissionError as e:
            # Database permission error
            error_msg = f"Database permission error: {str(e)}"
            print(error_msg)
            if 'doc_id' in locals():
                try:
                    self.db.update_document_status(doc_id, 'error')
                except:
                    pass  # Don't fail if we can't update status
            return False, error_msg
        except Exception as e:
            error_msg = f"Error processing PDF: {str(e)}"
            print(error_msg)
            # Check if it's a database readonly error
            if "readonly" in str(e).lower() or "read-only" in str(e).lower():
                error_msg = f"Database is read-only: {str(e)}. Please check file permissions."
            if 'doc_id' in locals():
                try:
                    self.db.update_document_status(doc_id, 'error')
                except:
                    pass  # Don't fail if we can't update status
            return False, error_msg
    
    def query_knowledge_base(self, query: str, n_results: int = 5) -> List[Dict]:
        """Query the knowledge base and return relevant chunks with metadata."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return formatted_results
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            return []
    
    def get_all_documents(self) -> List[str]:
        """Get list of all unique document sources in the knowledge base."""
        try:
            # Get all items from collection
            all_data = self.collection.get()
            sources = set()
            if all_data['metadatas']:
                for metadata in all_data['metadatas']:
                    if 'source' in metadata:
                        sources.add(metadata['source'])
            return list(sources)
        except Exception as e:
            print(f"Error getting documents: {e}")
            return []
    
    def delete_document(self, source_name: str):
        """Delete all chunks from a specific document."""
        try:
            all_data = self.collection.get()
            ids_to_delete = []
            
            if all_data['ids'] and all_data['metadatas']:
                for idx, metadata in enumerate(all_data['metadatas']):
                    if metadata.get('source') == source_name:
                        ids_to_delete.append(all_data['ids'][idx])
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                return True
            return False
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

