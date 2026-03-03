"""
Main entry point for SRAG RAG pipeline.
Demonstrates complete workflow from document loading to answer generation.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from srag import (
    DocumentProcessor,
    split_documents,
    EmbeddingManager,
    VectorStore,
    RAGRetriever,
    get_llm_backend,
    SRAGConfig,
)
from srag.logging_config import logger


def main():
    """Run the complete RAG pipeline."""
    try:
        logger.info("=" * 60)
        logger.info("Starting SRAG RAG Pipeline")
        logger.info("=" * 60)
        
        # Initialize configuration
        config = SRAGConfig()
        logger.info(f"Using configuration: chunk_size={config.chunk_size}, "
                   f"model={config.embedding_model}")
        
        # Step 1: Load documents
        logger.info("\n[Step 1] Loading documents...")
        loader = DocumentProcessor()
        documents = loader.load_text_files("./data/text_files")
        logger.info(f"✓ Loaded {len(documents)} documents")
        
        # Step 2: Split documents into chunks
        logger.info("\n[Step 2] Splitting documents into chunks...")
        chunks = split_documents(
            documents,
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
        logger.info(f"✓ Created {len(chunks)} chunks")
        
        # Step 3: Generate embeddings
        logger.info("\n[Step 3] Generating embeddings...")
        embedding_mgr = EmbeddingManager(model_name=config.embedding_model)
        texts = [doc.page_content for doc in chunks]
        embeddings = embedding_mgr.generate_embeddings(texts)
        logger.info(f"✓ Generated embeddings: shape {embeddings.shape}")
        
        # Step 4: Store in vector database
        logger.info("\n[Step 4] Storing embeddings in vector database...")
        vector_store = VectorStore(
            collection_name=config.collection_name,
            persist_directory=config.vector_db_path
        )
        vector_store.add_documents(chunks, embeddings)
        logger.info(f"✓ Stored {vector_store.get_count()} documents in vector store")
        
        # Step 5: Initialize retriever
        logger.info("\n[Step 5] Initializing retriever...")
        retriever = RAGRetriever(vector_store, embedding_mgr)
        logger.info("✓ Retriever ready")
        
        # Step 6: Get LLM backend
        logger.info("\n[Step 6] Initializing LLM backend...")
        llm = get_llm_backend(
            backend_type=config.llm_backend,
            model_name=config.llm_model
        )
        logger.info(f"✓ LLM backend ({config.llm_backend}) ready")
        
        # Step 7: Example query
        logger.info("\n" + "=" * 60)
        logger.info("Running example query...")
        logger.info("=" * 60)
        
        query = "What is vector embeddings?"
        logger.info(f"\nQuery: {query}\n")
        
        # Retrieve relevant documents
        logger.info("[7a] Retrieving relevant documents...")
        retrieved_docs = retriever.retrieve(
            query=query,
            top_k=config.top_k,
            score_threshold=config.similarity_threshold
        )
        
        # Build context from retrieved documents
        context = "\n\n".join([
            f"[Document {i+1}] {doc['content']}"
            for i, doc in enumerate(retrieved_docs)
        ])
        
        logger.info(f"[7b] Retrieved {len(retrieved_docs)} relevant documents")
        logger.info("\nRetrieved Documents:")
        for i, doc in enumerate(retrieved_docs):
            logger.info(f"  {i+1}. {doc['metadata'].get('source_file', 'Unknown')} "
                       f"(similarity: {doc['similarity_score']:.2%})")
        
        # Generate answer using LLM
        logger.info(f"\n[7c] Generating answer with {config.llm_model}...")
        answer = llm.generate_with_context(
            query=query,
            context=context
        )
        
        logger.info("\n" + "=" * 60)
        logger.info("ANSWER")
        logger.info("=" * 60)
        print("\n" + answer + "\n")
        
        logger.info("=" * 60)
        logger.info("RAG Pipeline completed successfully!")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
