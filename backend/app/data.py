CURRICULUM = [
 {"day":4,"module":"RAG","topic":"Retrieval-Augmented Generation"},
 {"day":7,"module":"RAG","topic":"Chunking and retrieval"},
 {"day":10,"module":"Vector Databases","topic":"Embeddings and vector search"},
 {"day":13,"module":"Prompt Engineering","topic":"Reliable prompting"},
 {"day":16,"module":"Agentic AI","topic":"AI agents"},
 {"day":19,"module":"MCP","topic":"Model Context Protocol"},
 {"day":22,"module":"AI Deployment","topic":"Serving AI applications"},
 {"day":25,"module":"Production AI Systems","topic":"Evaluation and monitoring"},
]

CANDIDATES = [
 {"id":"candidate-01","name":"Aarav Sharma","completed_days":[4,7,10,13,16,19,22],"skipped_days":[25],
  "signal":"Strong RAG and agent foundations; needs deeper production reasoning."},
 {"id":"candidate-02","name":"Palak","completed_days":[4,7,10,13,16,19],
  "skipped_days":[22,25],"signal":"Good conceptual coverage; probe deployment and production gaps."},
]

def candidate_by_id(cid):
    return next((c for c in CANDIDATES if c["id"] == cid), None)
