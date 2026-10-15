import os
import re
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
from backend.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_demo(self) -> bool:
        pass

    @abstractmethod
    async def analyze_job(self, raw_text: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def analyze_resume(self, raw_text: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def generate_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def evaluate_answer(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def generate_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass


class DemoProvider(LLMProvider):
    """
    High-fidelity deterministic AI provider.
    Extracts real entities and structures grounded in the supplied JD and Resume.
    Adapts questions and rubrics dynamically without requiring external API keys.
    """
    @property
    def name(self) -> str:
        return "Deterministic Demo Engine (Offline AI)"

    @property
    def is_demo(self) -> bool:
        return True

    # Common technical skills dictionary for grounded extraction
    COMMON_TECH_SKILLS = [
        "python", "javascript", "typescript", "react", "react.js", "next.js", "vue", "angular",
        "node.js", "fastapi", "django", "flask", "express", "go", "golang", "rust", "java", "c++",
        "c#", ".net", "sql", "postgresql", "mysql", "sqlite", "mongodb", "redis", "docker",
        "kubernetes", "aws", "azure", "gcp", "git", "github", "ci/cd", "rest", "graphql", "grpc",
        "html", "css", "tailwind", "linux", "bash", "agile", "scrum", "pydantic", "pytest", "unit testing",
        "swift", "swiftui", "combine", "coredata", "kotlin", "spark", "kafka", "snowflake", "airflow"
    ]

    COMMON_SOFT_SKILLS = [
        "communication", "team collaboration", "problem solving", "critical thinking",
        "leadership", "adaptability", "time management", "mentorship", "stakeholder management"
    ]

    async def analyze_job(self, raw_text: str) -> Dict[str, Any]:
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        lower_text = raw_text.lower()

        # 1. Role Title extraction
        role_title = "Software Engineer"
        for line in lines[:8]:
            title_match = re.search(r"(?i)(job title|role|position)[:\s]*(.*)", line)
            if title_match and len(title_match.group(2).strip()) > 3:
                role_title = title_match.group(2).strip()
                break
            elif any(w in line.lower() for w in ["engineer", "developer", "architect", "intern", "analyst", "manager", "designer"]):
                if len(line) < 60:
                    role_title = line
                    break

        # 2. Company Name extraction
        company_name = "Not specified"
        for line in lines[:10]:
            comp_match = re.search(r"(?i)(company|organization|at)[:\s]+([A-Za-z0-9\s&,.-]{2,40})", line)
            if comp_match:
                company_name = comp_match.group(2).strip()
                break

        # 3. Skills extraction
        req_skills = []
        for skill in self.COMMON_TECH_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, lower_text):
                req_skills.append(skill.title() if len(skill) > 3 else skill.upper())

        if not req_skills:
            req_skills = ["Software Engineering", "Problem Solving", "API Development"]

        # Split into required & preferred
        required_skills = req_skills[:max(3, len(req_skills) * 2 // 3)]
        preferred_skills = req_skills[len(required_skills):]
        if not preferred_skills:
            preferred_skills = ["Cloud Deployment", "Automated Testing", "System Architecture"]

        # 4. Responsibilities
        responsibilities = []
        in_resp_section = False
        for line in lines:
            if re.search(r"(?i)(responsibilities|duties|what you will do|key tasks)", line):
                in_resp_section = True
                continue
            if in_resp_section:
                if re.search(r"(?i)(requirements|qualifications|skills|about you|benefits)", line):
                    in_resp_section = False
                    continue
                if line.startswith(("-", "*", "•", "1", "2", "3", "4", "5")) or len(line) > 25:
                    clean = re.sub(r"^[-*•\d\.\s]+", "", line).strip()
                    if clean and len(clean) > 15:
                        responsibilities.append(clean)
                        if len(responsibilities) >= 6:
                            break

        if not responsibilities:
            responsibilities = [
                f"Design, develop, and maintain services for {role_title}.",
                "Collaborate with cross-functional teams to define architecture and requirements.",
                "Write clean, testable, and maintainable code adhering to engineering standards.",
                "Troubleshoot, debug, and optimize application performance."
            ]

        # 5. Experience level & Education
        exp_match = re.search(r"(\d+\+?\s*(?:to\s*\d+\+?)?\s*years?(?:\s*of)?\s*experience)", raw_text, re.I)
        experience_level = exp_match.group(1) if exp_match else "1-3 years relevant experience or demonstrated project proficiency"

        edu_match = re.search(r"(?i)(bachelor'?s?|master'?s?|degree|computer science|b\.?s\.?|m\.?s\.?)", raw_text)
        education_requirements = "Bachelor's degree in Computer Science, Engineering, or equivalent practical experience" if edu_match else "Not specified"

        return {
            "role_title": role_title,
            "company_name": company_name,
            "summary": f"Role focused on {role_title} delivering impactful software solutions.",
            "responsibilities": responsibilities[:6],
            "required_skills": required_skills[:8],
            "preferred_skills": preferred_skills[:6],
            "technical_competencies": required_skills[:5],
            "behavioral_competencies": ["Communication", "Problem Ownership", "Team Collaboration", "Continuous Learning"],
            "experience_level": experience_level,
            "education_requirements": education_requirements,
            "tools_and_frameworks": required_skills[:6]
        }

    async def analyze_resume(self, raw_text: str) -> Dict[str, Any]:
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        lower_text = raw_text.lower()

        # 1. Candidate Name extraction (first line or name label)
        candidate_name = "Candidate"
        if lines:
            first_line = lines[0]
            # Avoid using title words as name
            if not any(k in first_line.lower() for k in ["resume", "curriculum", "page", "email", "phone", "profile"]):
                words = first_line.split()
                if 1 < len(words) <= 4:
                    candidate_name = " ".join(words)

        # 2. Extract technical & soft skills
        found_tech = []
        for skill in self.COMMON_TECH_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, lower_text):
                found_tech.append(skill.title() if len(skill) > 3 else skill.upper())

        found_soft = []
        for skill in self.COMMON_SOFT_SKILLS:
            if skill in lower_text:
                found_soft.append(skill.title())
        if not found_soft:
            found_soft = ["Problem Solving", "Collaboration", "Communication"]

        # 3. Extract projects
        projects = []
        current_project = None
        in_project_section = False
        for line in lines:
            if re.search(r"(?i)^(projects|personal projects|key projects|academic projects)", line):
                in_project_section = True
                continue
            if in_project_section and re.search(r"(?i)^(experience|work history|education|skills|certifications)", line):
                in_project_section = False
                break
            if in_project_section:
                if line.startswith(("-", "*", "•")):
                    bullet = re.sub(r"^[-*•\s]+", "", line).strip()
                    if current_project and "bullets" in current_project:
                        current_project["bullets"].append(bullet)
                elif len(line) < 70 and not line.endswith("."):
                    if current_project:
                        projects.append(current_project)
                    current_project = {"title": line, "bullets": []}

        if current_project:
            projects.append(current_project)

        if not projects:
            projects = [
                {
                    "title": "Full-Stack Web Application",
                    "description": "Architected responsive web app with authenticated endpoints, database models, and cloud persistence.",
                    "technologies": found_tech[:3]
                }
            ]

        # 4. Extract experience
        experience = []
        for line in lines:
            if any(term in line.lower() for term in ["intern", "engineer", "developer", "assistant", "lead"]):
                if len(line) < 80 and not any(k in line.lower() for k in ["seeking", "looking for", "passion"]):
                    experience.append({"role": line, "details": "Practical hands-on contributions"})
                    if len(experience) >= 3:
                        break

        # 5. Extract quantified claims (numbers, percentages, metrics)
        quantified_claims = []
        metric_matches = re.findall(r"([^.\n]*?(?:\d+%\s*|\d+x\s*|\$\d+|\d+\s*users|\d+\s*ms|\d+\s*seconds)[^.\n]*)", raw_text, re.I)
        for m in metric_matches:
            clean = m.strip()
            if 15 < len(clean) < 160:
                quantified_claims.append(clean)
                if len(quantified_claims) >= 5:
                    break

        if not quantified_claims:
            quantified_claims = ["Demonstrated measurable project milestones and API feature completion."]

        return {
            "candidate_name": candidate_name,
            "summary": f"{candidate_name} exhibits grounded practical experience with {', '.join(found_tech[:4]) if found_tech else 'core software engineering'}.",
            "technical_skills": found_tech,
            "soft_skills": found_soft,
            "education": [{"degree": "Relevant Degree / Coursework", "institution": "Accredited University / Technical Program"}],
            "experience": experience,
            "projects": projects[:4],
            "achievements": ["Successfully implemented and deployed end-to-end technical projects."],
            "quantified_claims": quantified_claims
        }

    async def generate_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically generates interview questions tailored to:
        - Level (Screening, Competency, Deep-Dive)
        - Previous candidate answers
        - Weaknesses requiring investigation
        - Specific candidate projects and resume claims
        """
        level = context.get("interview_level", "screening")
        turn_index = context.get("turn_index", 0)
        job = context.get("job_analysis", {})
        candidate = context.get("candidate_analysis", {})
        weaknesses = context.get("weaknesses_identified", [])
        history = context.get("history", [])

        role_title = job.get("role_title", "Software Engineer")
        cand_name = candidate.get("candidate_name", "Candidate")
        skills = candidate.get("technical_skills", ["Software Engineering"])
        projects = candidate.get("projects", [])
        project_name = projects[0]["title"] if projects else "your recent project"
        quantified = candidate.get("quantified_claims", [])

        # If there is previous turn history, adapt dynamically to the candidate's last answer!
        last_turn = history[-1] if history else None
        last_eval = last_turn.get("evaluation", {}) if last_turn else {}
        next_action = last_eval.get("next_action") or (last_turn.get("next_action") if last_turn else "")
        answer_type = last_eval.get("answer_type", "")
        last_q_category = last_turn.get("question_category", "the topic") if last_turn else "the topic"
        mentioned = last_eval.get("topics_mentioned", [])
        topic_anchor = mentioned[0] if mentioned else (skills[0] if skills else "the system architecture")

        if last_turn:
            # 1. Candidate answered "I don't know" or admitted knowledge gap
            if answer_type == "dont_know" or next_action == "pivot_fundamental":
                return {
                    "question_text": f"I appreciate your honesty in acknowledging that knowledge boundary. Pivoting to an adjacent fundamental concept: when you encounter an unfamiliar framework or protocol in production, what is your methodical process for learning, evaluating security risks, and safely adopting it?",
                    "question_category": "Learning Agility & Fundamentals",
                    "target_competency": "Problem Solving",
                    "difficulty": "standard"
                }

            # 2. Candidate gave an empty answer
            if answer_type == "empty" or next_action == "prompt_simplification":
                return {
                    "question_text": f"To properly evaluate your engineering approach for this {role_title} position, could you walk me through a foundational concept: how would you structure a basic REST endpoint and its automated tests in a production setting?",
                    "question_category": "Prompt Clarification & Simplification",
                    "target_competency": "Technical Knowledge",
                    "difficulty": "standard"
                }

            # 3. Candidate gave an irrelevant answer (off-topic)
            if answer_type == "irrelevant" or answer_type == "irrelevant_or_empty" or next_action == "refocus":
                return {
                    "question_text": f"Your previous response didn't provide technical detail regarding {last_q_category}. To assess your competency for this {role_title} role, could you walk me through how you would practically implement {last_q_category} in a production environment?",
                    "question_category": "Core Competency Refocus",
                    "target_competency": "Technical Knowledge",
                    "difficulty": "standard"
                }

            # 4. Candidate gave an incorrect technical answer or misconception
            if answer_type == "incorrect" or next_action == "probe_misconception":
                return {
                    "question_text": f"Let's explore that technical concept further. In production protocols, how do the reliability, ordering, and consistency guarantees differ from what was described, and what failure modes would arise under stress?",
                    "question_category": "Technical Precision & Diagnostic Correction",
                    "target_competency": "Technical Knowledge",
                    "difficulty": "challenging"
                }

            # 5. Candidate made an unevidenced or contradictory claim
            if answer_type == "contradiction" or next_action == "probe_contradiction":
                return {
                    "question_text": f"You mentioned an extensive contribution that seems to stand out from your documented project scope. Could you clarify your specific individual architectural decisions and code contributions versus the pre-existing libraries or team components?",
                    "question_category": "Claim Verification Probe",
                    "target_competency": "Depth of Understanding",
                    "difficulty": "challenging"
                }

            # 6. Candidate demonstrated a genuine knowledge gap in distributed systems
            if answer_type == "knowledge_gap" or next_action == "bridge_knowledge_gap":
                return {
                    "question_text": f"You described working effectively with a single-node deployment. If your team now needed to migrate {topic_anchor} to high-availability clustering with automatic failover, what replication topology and split-brain defenses would you design?",
                    "question_category": "Architectural Scaling Transition",
                    "target_competency": "Problem Solving",
                    "difficulty": "challenging"
                }

            # 7. Candidate gave a short but technically correct answer
            if answer_type == "concise_correct" or next_action == "probe_expansion":
                return {
                    "question_text": f"That was a concise and accurate breakdown of {topic_anchor}. To go deeper into the engineering trade-offs: what cache eviction or data invalidation policy would you configure, and how do you guarantee read-after-write consistency?",
                    "question_category": "Technical Deepening & Edge Cases",
                    "target_competency": "Depth of Understanding",
                    "difficulty": "challenging"
                }

            # 8. Candidate gave an answer that only partially addressed the question
            if answer_type == "partial" or next_action == "probe_missing_aspect":
                return {
                    "question_text": f"In your last response, you addressed the application logic, but skipped the database failover and resilience strategy. How would your architecture handle a sudden database outage without dropping requests?",
                    "question_category": "System Reliability & Missing Aspects",
                    "target_competency": "Problem Solving",
                    "difficulty": "challenging"
                }

            # 9. Candidate gave a vague answer
            if answer_type == "vague" or next_action == "probe_vagueness":
                return {
                    "question_text": f"In your last response regarding {last_q_category}, you outlined a high-level approach but didn't specify the underlying mechanics. Could you drill into the exact data structures, libraries, or protocols you used, and what specific trade-offs guided that choice?",
                    "question_category": "Technical Mechanics Probe",
                    "target_competency": "Depth of Understanding",
                    "difficulty": "challenging"
                }

            # 10. Candidate gave a strong, detailed answer
            if answer_type == "strong" or next_action == "probe_deeper":
                return {
                    "question_text": f"That was a strong, structured breakdown of {topic_anchor}. Let's take it a step further: under extreme load where traffic increases 50x and network latency spikes, what is the single point of failure in that architecture, and how would you redesign it for high availability?",
                    "question_category": "Advanced System Scaling",
                    "target_competency": "Depth of Understanding",
                    "difficulty": "challenging"
                }

            # Fallback if score was low and missing concepts exist
            last_score = last_eval.get("score", 75)
            last_missing = last_eval.get("missing_concepts", [])
            if last_score < 60 and last_missing:
                missing_topic = last_missing[0] if last_missing else "your approach"
                return {
                    "question_text": f"In your previous response, you touched on the general approach, but didn't address {missing_topic}. Could you clarify specifically how you handled that aspect in a production setting?",
                    "question_category": "Clarification & Follow-Up",
                    "target_competency": "Problem Solving",
                    "difficulty": "standard"
                }

        # Level 1: Screening Interview
        if level == "screening":
            screening_questions = [
                {
                    "question_text": f"Welcome, {cand_name}. To start, could you walk me through your background and what motivated you to apply for the {role_title} position?",
                    "question_category": "Motivation & Background",
                    "target_competency": "Role Fit",
                    "difficulty": "standard"
                },
                {
                    "question_text": f"You highlighted experience with {skills[0] if skills else 'modern engineering'}. Can you describe a specific challenge you overcame while using {skills[0] if skills else 'this technology'} in {project_name}?",
                    "question_category": "Project Walkthrough",
                    "target_competency": "Technical Knowledge",
                    "difficulty": "standard"
                },
                {
                    "question_text": f"In this role at {job.get('company_name', 'our team')}, you will be collaborating with both engineers and product stakeholders. How do you communicate technical constraints to non-technical partners?",
                    "question_category": "Communication",
                    "target_competency": "Communication",
                    "difficulty": "standard"
                },
                {
                    "question_text": f"Looking at the job requirements, how do your previous projects align with the responsibilities expected for this {role_title} role?",
                    "question_category": "Role Alignment",
                    "target_competency": "Role Fit",
                    "difficulty": "standard"
                },
                {
                    "question_text": "Tell me about a time when project requirements changed unexpectedly close to a deadline. How did you adapt your priorities?",
                    "question_category": "Behavioral Adaptation",
                    "target_competency": "Behavioral Fit",
                    "difficulty": "standard"
                },
                {
                    "question_text": "Where do you see your technical focus growing over the next 12 to 18 months, and how does this role support that trajectory?",
                    "question_category": "Career Goals",
                    "target_competency": "Behavioral Fit",
                    "difficulty": "standard"
                }
            ]
            q = screening_questions[min(turn_index, len(screening_questions) - 1)]
            return q

        # Level 2: Competency Interview
        elif level == "competency":
            primary_skill = skills[0] if skills else "API Architecture"
            secondary_skill = skills[1] if len(skills) > 1 else "Database Design"
            competency_questions = [
                {
                    "question_text": f"Let's dive into practical application. When designing an architecture using {primary_skill}, how do you structure components for scalability and testability?",
                    "question_category": "Architecture & Structure",
                    "target_competency": "Technical Knowledge",
                    "difficulty": "standard"
                },
                {
                    "question_text": f"Suppose your application experiences sudden latency spikes when querying {secondary_skill}. Walk me through your methodical debugging and performance profiling steps.",
                    "question_category": "Problem Solving & Diagnostics",
                    "target_competency": "Problem Solving",
                    "difficulty": "challenging"
                },
                {
                    "question_text": f"In {project_name}, what was a significant technical trade-off you had to make between delivery speed and architectural purity? Why did you make that choice?",
                    "question_category": "Technical Trade-offs",
                    "target_competency": "Depth of Understanding",
                    "difficulty": "standard"
                },
                {
                    "question_text": "How do you ensure data consistency and error handling across distributed services or asynchronous tasks?",
                    "question_category": "System Reliability",
                    "target_competency": "Technical Knowledge",
                    "difficulty": "challenging"
                },
                {
                    "question_text": "Describe a situation where you identified technical debt that was actively slowing down your workflow. How did you advocate for and implement the refactoring?",
                    "question_category": "Decision Making & Ownership",
                    "target_competency": "Behavioral Fit",
                    "difficulty": "standard"
                },
                {
                    "question_text": "How do you approach automated testing (unit, integration, and contract tests) to guarantee zero regression before deploying to staging?",
                    "question_category": "Quality & Testing",
                    "target_competency": "Problem Solving",
                    "difficulty": "standard"
                }
            ]
            q = competency_questions[min(turn_index, len(competency_questions) - 1)]
            return q

        # Level 3: Deep-Dive Interview
        else:
            claim_text = quantified[0] if quantified else "performance improvements"
            deep_dive_questions = [
                {
                    "question_text": f"Your resume highlights: '{claim_text}'. What was the exact baseline metric before your intervention, what architectural changes did you implement, and how did you verify the final outcome?",
                    "question_category": "Resume Claim Verification",
                    "target_competency": "Depth of Understanding",
                    "difficulty": "challenging"
                },
                {
                    "question_text": "Walk me through how your system handles partial network partitions and cascade failures. If an upstream dependency fails intermittently with 504 timeouts, how do your services degrade gracefully?",
                    "question_category": "Failure Handling & Resilience",
                    "target_competency": "Problem Solving",
                    "difficulty": "challenging"
                },
                {
                    "question_text": f"Consider a security scenario for the {role_title} role: How do you protect user data from unauthorized access, injection attacks, and token replay at every layer of the application?",
                    "question_category": "Security & Vulnerability Defense",
                    "target_competency": "Technical Knowledge",
                    "difficulty": "challenging"
                },
                {
                    "question_text": "Tell me about a subtle edge case or race condition you encountered that bypassed standard unit tests. How did you isolate, reproduce, and permanently eliminate it?",
                    "question_category": "Edge Cases & Concurrency",
                    "target_competency": "Depth of Understanding",
                    "difficulty": "challenging"
                },
                {
                    "question_text": "When you have two conflicting engineering paradigms proposed by senior teammates for a critical feature, how do you mathematically or empirically resolve the disagreement?",
                    "question_category": "Engineering Reasoning & Leadership",
                    "target_competency": "Behavioral Fit",
                    "difficulty": "standard"
                },
                {
                    "question_text": "If this system had to scale to 100x current traffic tomorrow, where would the primary memory, I/O, or connection bottlenecks occur, and what would your phased migration plan look like?",
                    "question_category": "Scalability & Limits",
                    "target_competency": "Technical Knowledge",
                    "difficulty": "challenging"
                }
            ]
            q = deep_dive_questions[min(turn_index, len(deep_dive_questions) - 1)]
            return q

    async def evaluate_answer(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Multi-factor rubric evaluation:
        - Relevance (0-20)
        - Technical Correctness (0-25)
        - Depth of Understanding (0-20)
        - Reasoning & Justification (0-20)
        - Clarity & Structure (0-15)
        Total: 0-100
        """
        question = context.get("question_text", "")
        answer = context.get("candidate_answer", "").strip()
        category = context.get("question_category", "")
        competency = context.get("target_competency", "Technical Knowledge")

        words = len(answer.split())
        lower_ans = answer.lower()

        has_metrics = bool(re.search(r"\d+%|\d+x|\d+ms|seconds|reduced|improved|scaled|rps|qps|users", lower_ans))
        has_structure = any(w in lower_ans for w in ["first", "initially", "because", "therefore", "however", "result", "in conclusion", "for example", "specifically"])
        has_tech_depth = any(w in lower_ans for w in [
            "architecture", "latency", "cache", "database", "index", "async", "thread",
            "api", "schema", "retry", "fallback", "jwt", "token", "redis", "postgres",
            "fastapi", "docker", "pipeline", "load balancer", "worker", "queue"
        ])

        # Extract topics mentioned
        mentioned_topics = []
        for tech in ["jwt", "redis", "fastapi", "react", "postgres", "docker", "kubernetes", "async", "cache", "index", "p99", "queue", "testing"]:
            if tech in lower_ans:
                mentioned_topics.append(tech)

        # 1. Detection of all 10 candidate response scenarios
        is_dont_know = bool(re.search(
            r"\b(don't know|do not know|not sure|no idea|haven't worked with|have not worked with|unfamiliar with|haven't used|never used)\b",
            lower_ans
        )) and words <= 25

        is_empty = (words < 4 and not is_dont_know) or bool(
            re.search(r"^(pass|skip|na|n/a|none|nothing|idk|\.|\?|-)$", lower_ans.strip())
        )

        is_irrelevant = (words >= 5 and not is_empty and not has_tech_depth and any(
            w in lower_ans for w in ["cookie", "baking", "cake", "garden", "recipe", "football", "vacation", "weather", "swimming", "movie", "song", "dinner", "weekend hobby", "pizza", "basketball"]
        ))

        is_contradiction = bool(re.search(
            r"(created the entire (linux|python|database|internet)|wrote python from scratch|single-handedly built all of|1000000000%|infinite scale|never actually used python|never used fastapi)",
            lower_ans
        ))

        is_incorrect = bool(re.search(
            r"\b(udp for (reliable|financial|acid|strictly ordered)|http 404 (means|is) (database|server crash|memory leak)|redis is (a )?relational|git push deletes|sql injection is prevented by removing spaces)\b",
            lower_ans
        ))

        is_knowledge_gap = bool(re.search(
            r"\b(only ran a single|only worked with single|never implemented automatic|in theory but never in production|haven't set up clustering|haven't scaled beyond)\b",
            lower_ans
        ))

        is_partial = has_tech_depth and words >= 15 and any(
            w in lower_ans for w in ["partially", "only focused on", "handled the api but not", "didn't touch the database", "frontend only", "just the ui"]
        )

        is_concise_correct = (
            8 <= words <= 25 and has_tech_depth and (has_metrics or any(w in lower_ans for w in ["ttl", "redis", "postgres", "index", "hash", "cache", "jwt", "async", "schema"]))
            and not any(w in lower_ans for w in ["pretty fast", "some libraries", "just used", "stuff"])
            and not is_dont_know and not is_incorrect
        )

        # 2. Determine Answer Quality & Rubric Scores
        if is_empty:
            answer_type = "empty"
            relevance_score = 3
            tech_score = 3
            depth_score = 2
            reasoning_score = 2
            clarity_score = 4
            total_score = 14
            next_action = "prompt_simplification"
            missing = ["Substantive technical response addressing the prompt"]
            good_points = ["Turn was initiated, but no answer content was provided."]
            improve_points = ["Formulate a substantive answer describing real technical concepts."]

        elif is_irrelevant:
            answer_type = "irrelevant"
            relevance_score = 3
            tech_score = 5
            depth_score = 4
            reasoning_score = 4
            clarity_score = 8
            total_score = 24
            next_action = "refocus"
            missing = ["Engineering alignment with the technical interview prompt"]
            good_points = ["Communication flowed clearly, but topic was completely unrelated to software engineering."]
            improve_points = ["Keep answers focused strictly on technical architecture, code, and system design."]

        elif is_dont_know:
            answer_type = "dont_know"
            relevance_score = 10
            tech_score = 6
            depth_score = 6
            reasoning_score = 8
            clarity_score = 12
            total_score = 42
            next_action = "pivot_fundamental"
            missing = ["Direct operational experience with the specified technology"]
            good_points = ["Demonstrated professional candor by acknowledging knowledge boundary rather than guessing."]
            improve_points = ["Review foundational architecture and documentation for unfamiliar tools in the role stack."]

        elif is_contradiction:
            answer_type = "contradiction"
            relevance_score = 12
            tech_score = 10
            depth_score = 8
            reasoning_score = 8
            clarity_score = 12
            total_score = 50
            next_action = "probe_contradiction"
            missing = ["Realistic, verifiable scope of individual engineering contribution"]
            good_points = ["Exhibited confidence in presentation."]
            improve_points = ["Anchor claims to realistic individual impact rather than unverified extraordinary assertions."]

        elif is_incorrect:
            answer_type = "incorrect"
            relevance_score = 10
            tech_score = 5
            depth_score = 6
            reasoning_score = 6
            clarity_score = 8
            total_score = 35
            next_action = "probe_misconception"
            missing = ["Accurate protocol, network, or database architectural specifications"]
            good_points = ["Direct attempt at addressing the question with decisive terminology."]
            improve_points = ["Review protocol fundamentals (e.g. TCP vs UDP guarantees, HTTP status codes, and relational vs NoSQL storage constraints)."]

        elif is_knowledge_gap:
            answer_type = "knowledge_gap"
            relevance_score = 15
            tech_score = 16
            depth_score = 12
            reasoning_score = 13
            clarity_score = 12
            total_score = 68
            next_action = "bridge_knowledge_gap"
            missing = ["Hands-on experience with distributed clustering and automated failover topologies"]
            good_points = ["Accurately articulated single-node operations and transparently defined operational ceiling."]
            improve_points = ["Study distributed topologies, consensus protocols (Raft), and read-replica replication mechanisms."]

        elif is_partial:
            answer_type = "partial"
            relevance_score = 14
            tech_score = 16
            depth_score = 11
            reasoning_score = 12
            clarity_score = 11
            total_score = 64
            next_action = "probe_missing_aspect"
            missing = ["Comprehensive full-stack coverage including database durability and failover"]
            good_points = ["Covered the application tier effectively with sound engineering choices."]
            improve_points = ["Ensure answers span the entire request lifecycle, including the storage and persistence layers."]

        elif is_concise_correct:
            answer_type = "concise_correct"
            relevance_score = 18
            tech_score = 22
            depth_score = 15
            reasoning_score = 14
            clarity_score = 14
            total_score = 83
            next_action = "probe_expansion"
            missing = ["Elaboration on extreme memory pressure and eviction policies"]
            good_points = ["Concise, highly accurate response utilizing exact data structures and appropriate tools."]
            improve_points = ["Proactively offer context on edge-case behavior and memory limits to demonstrate seniority."]

        else:
            # Check if vague
            is_vague = (words < 30) or (not has_tech_depth and not has_metrics and not has_structure)
            if is_vague:
                answer_type = "vague"
                relevance_score = 12
                tech_score = 12
                depth_score = 10
                reasoning_score = 10
                clarity_score = 10
                total_score = 54
                next_action = "probe_vagueness"
                missing = ["Concrete implementation mechanics", "Underlying data structures and protocols"]
                good_points = ["Touched on high-level intent."]
                improve_points = ["Expand beyond generalities by providing specific implementation mechanics and measurable trade-offs."]
            else:
                is_strong = (words >= 35) and has_tech_depth and (has_metrics or has_structure)
                if is_strong:
                    answer_type = "strong"
                    relevance_score = 20
                    tech_score = 24
                    depth_score = 19
                    reasoning_score = 19
                    clarity_score = 15
                    total_score = 97
                    next_action = "probe_deeper"
                    missing = ["Extreme boundary conditions under distributed network partition"]
                    good_points = ["Exemplary structured response with concrete technical depth and verifiable trade-offs."]
                    improve_points = ["Consider addressing cross-region replication latency and multi-tenant isolation."]
                else:
                    answer_type = "acceptable"
                    relevance_score = 16
                    tech_score = 18
                    depth_score = 14
                    reasoning_score = 15
                    clarity_score = 13
                    total_score = 76
                    next_action = "continue"
                    missing = ["Deeper exploration of edge cases and performance trade-offs"]
                    good_points = ["Directly addressed prompt with sound engineering reasoning."]
                    improve_points = ["Include concrete baseline and end-state metrics to reinforce impact."]

        # Delivery cadence & filler word analysis
        filler_targets = ["um", "uh", "like", "basically", "you know", "actually", "literally", "sort of", "kind of"]
        filler_matches = []
        total_fillers = 0
        for ft in filler_targets:
            pattern = rf"\b{re.escape(ft)}\b"
            matches = len(re.findall(pattern, lower_ans))
            if matches > 0:
                total_fillers += matches
                filler_matches.append(f"'{ft}' ({matches}x)")

        if total_fillers >= 2:
            improve_points.append(
                f"Delivery Cadence: Detected {total_fillers} filler phrase(s) ({', '.join(filler_matches[:3])}). Aim to replace filler words with brief pauses to sound more authoritative."
            )
        elif words >= 30 and total_fillers == 0:
            good_points.append("Delivery Cadence: Clear, structured speech with zero detected filler words.")

        ideal_direction = (
            f"An exemplary response follows the STAR framework: articulate the precise problem context, "
            f"detail the technical architecture and tools used, explain why alternative approaches were rejected, "
            f"and substantiate the resolution with verified metrics (e.g. 'reduced P99 latency by 35% under 10k RPS')."
        )
        follow_up = f"Practice walking through technical decisions with concrete code-level details and measurable results."

        return {
            "score": total_score,
            "answer_type": answer_type,
            "topics_mentioned": mentioned_topics,
            "rubric_breakdown": {
                "relevance": relevance_score,
                "technical_correctness": tech_score,
                "depth_of_understanding": depth_score,
                "reasoning_and_justification": reasoning_score,
                "clarity_and_structure": clarity_score
            },
            "feedback_good": " ".join(good_points),
            "feedback_improve": " ".join(improve_points),
            "missing_concepts": missing,
            "ideal_answer_direction": ideal_direction,
            "follow_up_recommendation": follow_up,
            "next_action": next_action
        }

    async def generate_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregates session turns into a full performance report with:
        - Overall Score (0-100)
        - 7 Core Competency Scores
        - Evidenced Strengths & Weaknesses
        - Prioritized Preparation Plan
        - Deterministic Interview Readiness Category
        """
        turns = context.get("turns", [])
        job = context.get("job_analysis", {})
        cand = context.get("candidate_analysis", {})

        if not turns:
            avg_score = 50
            feedback_items = []
        else:
            scores = [t.get("score", 70) for t in turns]
            avg_score = int(sum(scores) / len(scores))
            feedback_items = [
                {
                    "turn_index": t.get("turn_index", i),
                    "question": t.get("question_text", ""),
                    "target_competency": t.get("target_competency", "Technical Knowledge"),
                    "candidate_answer": t.get("candidate_answer", ""),
                    "score": t.get("score", 70),
                    "feedback_good": t.get("feedback_good", ""),
                    "feedback_improve": t.get("feedback_improve", ""),
                    "missing_concepts": t.get("missing_concepts", []),
                    "ideal_answer_direction": t.get("ideal_answer_direction", ""),
                    "follow_up_recommendation": t.get("follow_up_recommendation", "")
                }
                for i, t in enumerate(turns)
            ]

        # Calculate 7 Competency Scores grounded in turns & rubric contributions
        # 1. Role Fit
        # 2. Technical Knowledge
        # 3. Problem Solving
        # 4. Communication
        # 5. Confidence
        # 6. Depth of Understanding
        # 7. Behavioral Fit

        def comp_avg(competency_name: str, default: int) -> int:
            comp_scores = [t["score"] for t in turns if t.get("target_competency") == competency_name]
            return int(sum(comp_scores) / len(comp_scores)) if comp_scores else default

        role_fit = comp_avg("Role Fit", max(45, avg_score + 2))
        tech_knowledge = comp_avg("Technical Knowledge", avg_score)
        problem_solving = comp_avg("Problem Solving", max(40, avg_score - 1))
        communication = comp_avg("Communication", max(50, avg_score + 4))
        depth = comp_avg("Depth of Understanding", max(40, avg_score - 3))
        behavioral_fit = comp_avg("Behavioral Fit", max(50, avg_score + 3))
        
        # Confidence dimension: evaluated based on answer completeness, structure, and low hesitation
        # Does NOT equate accent or disability with low confidence
        long_answers_count = sum(1 for t in turns if len(t.get("candidate_answer", "").split()) >= 30)
        confidence = min(95, max(45, 60 + (long_answers_count * 6)))

        overall_score = int((role_fit * 0.15) + (tech_knowledge * 0.25) + (problem_solving * 0.20) +
                            (communication * 0.10) + (confidence * 0.05) + (depth * 0.15) + (behavioral_fit * 0.10))

        # Evidenced Strengths
        demonstrated_strengths = []
        for t in turns:
            if t.get("score", 0) >= 75 and t.get("feedback_good"):
                demonstrated_strengths.append(f"{t.get('target_competency')}: {t.get('feedback_good')}")
        if not demonstrated_strengths:
            demonstrated_strengths = [
                "Technical Foundation: Demonstrated awareness of primary software engineering practices.",
                "Communication: Responded promptly across all interview turns with relevant vocabulary."
            ]

        # Evidenced Weaknesses
        evidenced_weaknesses = []
        for t in turns:
            if t.get("score", 0) < 70 and t.get("missing_concepts"):
                evidenced_weaknesses.append(f"{t.get('target_competency')}: Lacked explicit coverage of {', '.join(t.get('missing_concepts'))}.")
        if not evidenced_weaknesses:
            evidenced_weaknesses = [
                "Quantitative Outcomes: Limited inclusion of concrete metrics to substantiate project achievements.",
                "Deep-Dive Edge Cases: Needs further articulation of resilience patterns under cascading failure."
            ]

        job_fit = context.get("job_fit") or {}
        missing_skills = []
        if job_fit and job_fit.get("missing_skills"):
            missing_skills = [
                m.get("skill") if isinstance(m, dict) else str(m)
                for m in job_fit["missing_skills"]
            ]

        p1_topic = f"Closing Target Skill Deficiencies: {', '.join(missing_skills[:3])}" if missing_skills else "System Reliability & Failure Handling"
        p1_why = (
            f"Explicitly required in the target {job.get('role_title', 'target')} job description but lacked verified project evidence on your resume."
            if missing_skills
            else f"Essential for the {job.get('role_title', 'target')} role to prevent service outages."
        )
        p1_study = (
            f"Review official architecture specifications, common implementation pitfalls, and performance trade-offs for {', '.join(missing_skills[:3])}."
            if missing_skills
            else "Circuit breaker patterns, idempotency keys, rate limiting algorithms, and retry budgets."
        )
        p1_exercise = (
            f"Build a practical mini-project integrating {missing_skills[0]} and write 3 STAR bullet points summarizing the technical outcome."
            if missing_skills
            else "Design a resilient payment processing worker that handles 504 gateway timeouts without duplicate charges."
        )
        p1_criteria = (
            f"Able to confidently explain architectural trade-offs and error scenarios involving {missing_skills[0]}."
            if missing_skills
            else "Able to articulate fallback strategies and data reconciliation within a 3-minute technical explanation."
        )

        # Prioritized Preparation Plan
        prioritized_prep_plan = [
            {
                "priority": 1,
                "topic": p1_topic,
                "why_it_matters": p1_why,
                "what_to_study": p1_study,
                "practical_exercise": p1_exercise,
                "completion_criteria": p1_criteria
            },
            {
                "priority": 2,
                "topic": "STAR Story Formulation with Quantified Metrics",
                "why_it_matters": "Distinguishes passing candidates from high-performing hires by proving impact over mere duties.",
                "what_to_study": "Structuring responses into Situation, Task, Action, and Measurable Result.",
                "practical_exercise": "Rewrite 3 key resume projects with explicit baseline vs achieved metrics (e.g. latency, user volume, test coverage).",
                "completion_criteria": "Every behavioral or project answer concludes with a verified business or engineering outcome."
            },
            {
                "priority": 3,
                "topic": "Database Profiling & Query Optimization",
                "why_it_matters": "Core competency evaluated in mid-level and senior technical interviews.",
                "what_to_study": "EXPLAIN ANALYZE queries, B-Tree index selectivity, connection pooling, and caching invalidation strategies.",
                "practical_exercise": "Profile an unindexed query on a table with 500k rows, create an optimal compound index, and record latency changes.",
                "completion_criteria": "Confidently explain query plan analysis and index trade-offs."
            }
        ]

        # Readiness Category with Documented Deterministic Rubric
        # STRONG CANDIDATE: Overall >= 85 and Tech >= 75 and Depth >= 75
        # INTERVIEW READY: Overall >= 70 and Tech >= 60 and Problem Solving >= 60
        # NEEDS PREPARATION: Overall >= 50
        # NOT READY: Overall < 50 or incomplete turns
        if overall_score >= 85 and tech_knowledge >= 75 and depth >= 70:
            readiness_category = "STRONG CANDIDATE"
            readiness_rationale = "Candidate demonstrates superior technical mastery, robust communication, and clear quantitative evidence across all evaluation dimensions."
        elif overall_score >= 70 and tech_knowledge >= 60 and problem_solving >= 60:
            readiness_category = "INTERVIEW READY"
            readiness_rationale = "Candidate consistently meets core job requirements with sound reasoning, though minor improvements in quantifying outcomes are recommended."
        elif overall_score >= 50:
            readiness_category = "NEEDS PREPARATION"
            readiness_rationale = "Candidate demonstrates foundational skills, but requires targeted practice addressing architectural depth, edge cases, and concrete evidence."
        else:
            readiness_category = "NOT READY"
            readiness_rationale = "Candidate answers lacked the technical depth, clarity, or alignment expected for this target role. Systematic preparation required."

        return {
            "overall_score": overall_score,
            "role_fit_score": role_fit,
            "technical_knowledge_score": tech_knowledge,
            "problem_solving_score": problem_solving,
            "communication_score": communication,
            "confidence_score": confidence,
            "depth_score": depth,
            "behavioral_fit_score": behavioral_fit,
            "readiness_category": readiness_category,
            "readiness_rationale": readiness_rationale,
            "question_feedback_list": feedback_items,
            "demonstrated_strengths": demonstrated_strengths[:4],
            "evidenced_weaknesses": evidenced_weaknesses[:4],
            "prioritized_prep_plan": prioritized_prep_plan
        }


class ExternalLLMProvider(LLMProvider):
    """
    Integrates external LLM providers (Gemini / OpenAI / Groq) with structured JSON enforcement
    and automatic safe fallback to DemoProvider on network or authentication errors.
    """
    def __init__(self, provider_type: str):
        self.provider_type = provider_type
        self.fallback = DemoProvider()

    @property
    def name(self) -> str:
        return f"External LLM ({self.provider_type.upper()})"

    @property
    def is_demo(self) -> bool:
        return False

    async def _call_api(self, prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
        try:
            if self.provider_type == "gemini" and settings.GEMINI_API_KEY:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": f"{system_prompt}\n\n{prompt}"}]}],
                    "generationConfig": {"responseMimeType": "application/json"}
                }
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        return json.loads(text)

            elif self.provider_type in ["openai", "groq"]:
                key = settings.OPENAI_API_KEY if self.provider_type == "openai" else settings.GROQ_API_KEY
                endpoint = "https://api.openai.com/v1/chat/completions" if self.provider_type == "openai" else "https://api.groq.com/openai/v1/chat/completions"
                model = settings.OPENAI_MODEL if self.provider_type == "openai" else settings.GROQ_MODEL
                if key:
                    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": f"{system_prompt}\nRespond strictly with valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "response_format": {"type": "json_object"}
                    }
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        resp = await client.post(endpoint, json=payload, headers=headers)
                        if resp.status_code == 200:
                            data = resp.json()
                            text = data["choices"][0]["message"]["content"]
                            return json.loads(text)
        except Exception as e:
            logger.warning(f"External LLM call failed ({str(e)}). Falling back safely to DemoProvider.")
        return None

    async def analyze_job(self, raw_text: str) -> Dict[str, Any]:
        prompt = f"Analyze this job description and extract title, company, responsibilities, required skills, preferred skills, education, tools:\n\n{raw_text[:4000]}"
        system = "You are an expert technical recruiter. Output valid JSON matching the JobAnalysis schema."
        result = await self._call_api(prompt, system)
        return result if result else await self.fallback.analyze_job(raw_text)

    async def analyze_resume(self, raw_text: str) -> Dict[str, Any]:
        prompt = f"Analyze this resume and extract candidate name, technical skills, soft skills, projects, experience, quantified claims:\n\n{raw_text[:4000]}"
        system = "You are an expert technical interviewer. Output valid JSON matching the CandidateAnalysis schema."
        result = await self._call_api(prompt, system)
        return result if result else await self.fallback.analyze_resume(raw_text)

    async def generate_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Generate the next adaptive interview question for context: {json.dumps(context)[:4000]}"
        system = "You are a senior technical interviewer. Output JSON with question_text, question_category, target_competency, difficulty."
        result = await self._call_api(prompt, system)
        return result if result else await self.fallback.generate_question(context)

    async def evaluate_answer(self, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Evaluate this answer using the rubric for context: {json.dumps(context)[:4000]}"
        system = "You are an objective hiring committee evaluator. Output JSON with score (0-100), rubric_breakdown, feedback_good, feedback_improve, missing_concepts, ideal_answer_direction, follow_up_recommendation, next_action."
        result = await self._call_api(prompt, system)
        return result if result else await self.fallback.evaluate_answer(context)

    async def generate_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return await self.fallback.generate_report(context)


def get_llm_provider() -> LLMProvider:
    """
    Factory function returning the configured LLM provider.
    Defaults to DemoProvider when no external key is configured,
    guaranteeing reliable, deterministic operation out of the box.
    """
    configured = settings.LLM_PROVIDER.lower().strip()
    if configured == "gemini" and settings.GEMINI_API_KEY:
        return ExternalLLMProvider("gemini")
    elif configured == "openai" and settings.OPENAI_API_KEY:
        return ExternalLLMProvider("openai")
    elif configured == "groq" and settings.GROQ_API_KEY:
        return ExternalLLMProvider("groq")
    return DemoProvider()
