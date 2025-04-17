def prepare_questions(raw_questions):
    prepared = []
    for q_idx, q in enumerate(raw_questions):
        question_data = {
            "id": f"q{q_idx}",
            "question": q["question"],
            "answers": []
        }
        for a_idx, answer in enumerate(q["answers"]):
            answer_id = f"{question_data['id']}_a{a_idx}"
            question_data["answers"].append({
                "id": answer_id,
                "value": answer
            })
        prepared.append(question_data)
    return prepared