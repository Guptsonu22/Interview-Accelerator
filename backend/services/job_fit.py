import re
from typing import Dict, Any, List, Set, Tuple


class JobFitService:
    """
    Deterministic and explainable Job Fit Scoring Engine.
    Evaluates alignment between Job Requirements and Candidate Resume Evidence across 5 dimensions:
    - Required Skills Alignment (35%)
    - Preferred Skills Alignment (15%)
    - Project Evidence Alignment (20%)
    - Responsibilities Alignment (15%)
    - Experience & Qualification Alignment (15%)
    """

    @staticmethod
    def _normalize_skill(skill: str) -> str:
        s = skill.lower().strip()
        s = re.sub(r'[\.\-\_]', '', s)
        # Aliases
        aliases = {
            "reactjs": "react",
            "nodejs": "node",
            "golang": "go",
            "postgres": "postgresql",
            "typescript": "ts",
            "javascript": "js",
            "k8s": "kubernetes"
        }
        return aliases.get(s, s)

    @classmethod
    def calculate_job_fit(cls, job_analysis: Dict[str, Any], candidate_analysis: Dict[str, Any]) -> Dict[str, Any]:
        req_skills: List[str] = job_analysis.get("required_skills", [])
        pref_skills: List[str] = job_analysis.get("preferred_skills", [])
        responsibilities: List[str] = job_analysis.get("responsibilities", [])
        
        cand_tech: List[str] = candidate_analysis.get("technical_skills", [])
        cand_soft: List[str] = candidate_analysis.get("soft_skills", [])
        cand_projects: List[Dict[str, Any]] = candidate_analysis.get("projects", [])
        cand_exp: List[Dict[str, Any]] = candidate_analysis.get("experience", [])
        cand_claims: List[str] = candidate_analysis.get("quantified_claims", [])

        # Build normalized set of candidate evidence
        cand_skill_set = {cls._normalize_skill(s) for s in cand_tech}
        cand_all_text = " ".join([
            " ".join(cand_tech),
            " ".join(cand_soft),
            " ".join(cand_claims),
            " ".join(p.get("title", "") + " " + " ".join(p.get("bullets", [])) if isinstance(p, dict) else str(p) for p in cand_projects),
            " ".join(e.get("role", "") + " " + e.get("details", "") if isinstance(e, dict) else str(e) for e in cand_exp)
        ]).lower()

        # 1. Evaluate Required Skills (35%)
        matched_required = []
        partial_required = []
        missing_required = []

        for skill in req_skills:
            norm = cls._normalize_skill(skill)
            if norm in cand_skill_set or re.search(r'\b' + re.escape(norm) + r'\b', cand_all_text):
                matched_required.append({
                    "skill": skill,
                    "status": "demonstrated",
                    "importance": "required",
                    "evidence": f"Explicitly listed or demonstrated in candidate background."
                })
            elif any(part in norm for part in cand_skill_set if len(part) >= 3):
                partial_required.append({
                    "skill": skill,
                    "status": "partial",
                    "importance": "required",
                    "evidence": f"Related foundational concepts evidenced in profile."
                })
            else:
                missing_required.append({
                    "skill": skill,
                    "status": "missing",
                    "importance": "required",
                    "evidence": "Not explicitly evidenced in the supplied resume."
                })

        num_req = max(1, len(req_skills))
        req_score = int(((len(matched_required) * 1.0) + (len(partial_required) * 0.5)) / num_req * 100)
        req_score = min(100, max(0, req_score))

        # 2. Evaluate Preferred Skills (15%)
        matched_pref = []
        partial_pref = []
        missing_pref = []

        for skill in pref_skills:
            norm = cls._normalize_skill(skill)
            if norm in cand_skill_set or re.search(r'\b' + re.escape(norm) + r'\b', cand_all_text):
                matched_pref.append({
                    "skill": skill,
                    "status": "demonstrated",
                    "importance": "preferred",
                    "evidence": "Mentioned or evidenced in candidate work."
                })
            elif any(part in norm for part in cand_skill_set if len(part) >= 3):
                partial_pref.append({
                    "skill": skill,
                    "status": "partial",
                    "importance": "preferred",
                    "evidence": "Partial exposure indicated."
                })
            else:
                missing_pref.append({
                    "skill": skill,
                    "status": "missing",
                    "importance": "preferred",
                    "evidence": "Not evidenced in resume."
                })

        num_pref = max(1, len(pref_skills))
        pref_score = int(((len(matched_pref) * 1.0) + (len(partial_pref) * 0.5)) / num_pref * 100)
        pref_score = min(100, max(0, pref_score))

        # 3. Project Evidence Alignment (20%)
        # Evaluates presence of technical projects with actual technology mentions
        if not cand_projects:
            project_score = 0
        else:
            project_score = 30 + min(40, len(cand_projects) * 15)
            if any(cls._normalize_skill(req) in cand_all_text for req in req_skills):
                project_score += 30
            project_score = min(100, project_score)

        # 4. Responsibilities Alignment (15%)
        matched_resp_count = 0
        for resp in responsibilities:
            resp_words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', resp)]
            overlap = [w for w in resp_words if w in cand_all_text]
            if len(overlap) >= 2:
                matched_resp_count += 1
        num_resp = max(1, len(responsibilities))
        if matched_resp_count == 0:
            resp_score = 0
        else:
            resp_score = min(100, int((matched_resp_count / num_resp) * 100))

        # 5. Experience & Qualification Alignment (15%)
        if not cand_exp and not candidate_analysis.get("education"):
            exp_score = 0
        else:
            exp_score = 20
            if cand_exp:
                exp_score += min(50, len(cand_exp) * 20)
            if candidate_analysis.get("education"):
                exp_score += 30
            exp_score = min(100, exp_score)

        # Weighted Overall Score (0-100)
        overall_score = int(
            (req_score * 0.35) +
            (pref_score * 0.15) +
            (project_score * 0.20) +
            (resp_score * 0.15) +
            (exp_score * 0.15)
        )
        overall_score = min(100, max(0, overall_score))

        # Categorical reasons
        key_reasons = []
        if matched_required:
            skills_sample = [s["skill"] if isinstance(s, dict) else str(s) for s in matched_required[:3]]
            key_reasons.append(f"Strong demonstrated alignment in {len(matched_required)} required competencies including {', '.join(skills_sample)}.")
        if missing_required:
            missing_sample = [s["skill"] if isinstance(s, dict) else str(s) for s in missing_required[:3]]
            key_reasons.append(f"Missing explicit resume proof for {len(missing_required)} core requirements ({', '.join(missing_sample)}).")
        if cand_projects:
            key_reasons.append(f"Relevant project portfolio supports hands-on application of modern tech stack.")
        if not key_reasons:
            key_reasons.append("Baseline alignment established across foundational engineering skills.")

        # Preparation Topics
        prep_topics = [s["skill"] if isinstance(s, dict) else str(s) for s in missing_required] + [
            s["skill"] if isinstance(s, dict) else str(s) for s in partial_required
        ]
        if not prep_topics:
            prep_topics = [s["skill"] if isinstance(s, dict) else str(s) for s in req_skills[:3]]

        return {
            "overall_score": overall_score,
            "required_skills_score": req_score,
            "preferred_skills_score": pref_score,
            "project_evidence_score": project_score,
            "experience_score": exp_score,
            "responsibility_score": resp_score,
            "category_breakdown": {
                "required_skills": {"weight": "35%", "score": req_score},
                "preferred_skills": {"weight": "15%", "score": pref_score},
                "project_evidence": {"weight": "20%", "score": project_score},
                "responsibilities": {"weight": "15%", "score": resp_score},
                "experience_and_education": {"weight": "15%", "score": exp_score}
            },
            "matched_skills": matched_required + matched_pref,
            "partial_skills": partial_required + partial_pref,
            "missing_skills": missing_required + missing_pref,
            "key_reasons": key_reasons,
            "preparation_topics": prep_topics[:6]
        }
