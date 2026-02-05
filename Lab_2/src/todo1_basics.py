from typing import List, Dict

def normalize_scores(scores: List[int]) -> List[int]:
    """
    Return a new list where each score is clamped to the range [0, 100].
    """
    normalized = []
    for score in scores:
        if score > 100:
            normalized.append(100)
        elif score < 0:
            normalized.append(0)
        else:
            normalized.append(score)
    return normalized

def letter_grades(scores: List[int]) -> List[str]:
    """
    Convert numeric scores to letter grades after normalizing them.
    """
    # Step 1: Normalize the scores first as requested
    clean_scores = normalize_scores(scores)
    letters = []
    
    # Step 2: Determine letter grade based on the scale
    for score in clean_scores:
        if score >= 90:
            letters.append("A")
        elif score >= 80:
            letters.append("B")
        elif score >= 70:
            letters.append("C")
        elif score >= 60:
            letters.append("D")
        else:
            letters.append("F")
            
    return letters

def grade_histogram(grades: List[str]) -> Dict[str, int]:
    """
    Return a dictionary mapping each letter in {"A","B","C","D","F"} to its count.
    """
    # Initialize the dictionary with zeros for all possible grades
    histogram = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    
    for grade in grades:
        if grade in histogram:
            histogram[grade] += 1
            
    return histogram