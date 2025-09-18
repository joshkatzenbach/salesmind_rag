"""
Test script to verify chunking and batching functionality.
"""

def test_chunking_and_batching():
    """Test the chunking service with batching."""
    
    # Create a large text to test chunking
    large_text = """
    This is a sample transcript for testing the chunking service with batching.
    It contains multiple paragraphs and sentences to test the chunking logic.
    
    The chunking service should split this text into appropriate chunks
    based on the configured chunk size and overlap parameters.
    
    This is another paragraph to test the chunking functionality.
    It should be split intelligently based on the text structure.
    
    """ * 50  # Repeat to create a large text
    
    print("Testing ChunkingService with batching...")
    print(f"Input text length: {len(large_text)} characters")
    
    try:
        # Create service with small chunk size for testing
        from chunking_service import ChunkingService
        
        service = ChunkingService.__new__(ChunkingService)
        service.chunk_size = 200  # Small chunks for testing
        service.chunk_overlap = 50
        service.MAX_BATCH_SIZE = 5  # Small batch size for testing
        
        # Test chunking
        chunks = service.chunk_text(large_text)
        print(f"✅ Chunking successful. Created {len(chunks)} chunks")
        
        # Test batching logic (without actual API call)
        batch_count = 0
        for i in range(0, len(chunks), service.MAX_BATCH_SIZE):
            batch_chunks = chunks[i:i + service.MAX_BATCH_SIZE]
            batch_count += 1
            print(f"  Batch {batch_count}: {len(batch_chunks)} chunks")
        
        print(f"✅ Batching successful. Would process {len(chunks)} chunks in {batch_count} batches")
        
        # Test chunk statistics
        from models import Chunk
        chunk_objects = [Chunk(id=i, transcript_id=1, chunk_index=i, chunk_text=chunk, embedding=[]) for i, chunk in enumerate(chunks)]
        stats = service.get_chunk_stats(chunk_objects)
        
        print(f"✅ Chunk statistics: {stats}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\nBatching test completed!")

if __name__ == "__main__":
    test_chunking_and_batching()
