from tools.retrieval import rule_search_misra, rule_search_do178c, kb_citation
def retrieve_rules(question: str):
    misra_hits = rule_search_misra(question, top_k=6).get("hits", [])
    do_hits    = rule_search_do178c("objectives for: " + question, top_k=4).get("hits", [])
    ids = [h["rule_id"] for h in misra_hits] + [h["rule_id"] for h in do_hits]
    rules_json = kb_citation(ids)["rules_json"]
    return misra_hits + do_hits, rules_json
