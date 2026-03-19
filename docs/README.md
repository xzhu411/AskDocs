# Evaluation Sample Dataset

This directory contains sample evaluation data for testing the RAG system.

Format:
```json
{
  "query": "User question",
  "ground_truth": "Expected answer",
  "example_context": "Sample context that would be retrieved"
}
```

To add more evaluation cases:
1. Create a JSON file with the structure above
2. Run evaluation pipeline
3. Monitor metrics

See docs/DEVELOPMENT.md for how to run evaluations.
