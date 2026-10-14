from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from backend.schemas.reports import PerformanceReportResponse
from backend.services.report_generator import ReportGeneratorService

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/{session_id}", response_model=PerformanceReportResponse)
async def get_performance_report(session_id: str):
    try:
        report = await ReportGeneratorService.get_or_generate_report(session_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate report: {str(e)}")


@router.get("/{session_id}/export")
async def export_report_markdown(session_id: str, format: str = Query(default="markdown")):
    try:
        report = await ReportGeneratorService.get_or_generate_report(session_id)
        if format.lower() == "markdown":
            md = [
                f"# Interview Performance Report — {report.get('role_title', 'Software Role')}",
                f"**Candidate:** {report.get('candidate_name', 'Candidate')}  ",
                f"**Overall Interview Score:** {report['overall_score']} / 100  ",
                f"**Readiness Status:** {report['readiness_category']}  ",
                f"**Job Fit Assessment:** {report.get('job_fit_score', 'N/A')}%  \n",
                f"## Executive Assessment",
                f"{report['readiness_rationale']}\n",
                f"## Competency Breakdown",
                f"| Competency | Score (0-100) | Assessment |",
                f"| :--- | :---: | :--- |",
                f"| Role Fit | {report['role_fit_score']} | Alignment with role requirements |",
                f"| Technical Knowledge | {report['technical_knowledge_score']} | Correctness and conceptual clarity |",
                f"| Problem Solving | {report['problem_solving_score']} | Diagnostics and solution formulation |",
                f"| Communication | {report['communication_score']} | Clarity, structure, and conciseness |",
                f"| Confidence | {report['confidence_score']} | Certainty and low hesitation |",
                f"| Depth of Understanding | {report['depth_score']} | Architectural nuance & trade-offs |",
                f"| Behavioral Fit | {report['behavioral_fit_score']} | Ownership and team adaptability |\n",
                f"## Demonstrated Strengths",
            ]
            for s in report.get("demonstrated_strengths", []):
                md.append(f"- **{s}**")

            md.append("\n## Evidenced Weaknesses & Knowledge Gaps")
            for w in report.get("evidenced_weaknesses", []):
                md.append(f"- {w}")

            md.append("\n## Question-Level Evaluations")
            for qf in report.get("question_feedback_list", []):
                md.append(f"### Question {qf['turn_index'] + 1}: {qf['question']}")
                md.append(f"- **Candidate Answer:** \"{qf['candidate_answer']}\"")
                md.append(f"- **Score:** {qf['score']} / 100")
                md.append(f"- **What Was Good:** {qf['feedback_good']}")
                md.append(f"- **What Could Be Improved:** {qf['feedback_improve']}")
                if qf.get("missing_concepts"):
                    md.append(f"- **Missing Concepts:** {', '.join(qf['missing_concepts'])}")
                md.append(f"- **Ideal Answer Direction:** {qf['ideal_answer_direction']}")
                md.append(f"- **Practice Recommendation:** {qf['follow_up_recommendation']}\n")

            md.append("\n## Prioritized Preparation Roadmap")
            for plan in report.get("prioritized_prep_plan", []):
                md.append(f"### Priority {plan['priority']}: {plan['topic']}")
                md.append(f"- **Why It Matters:** {plan['why_it_matters']}")
                md.append(f"- **What To Study:** {plan['what_to_study']}")
                md.append(f"- **Practical Exercise:** {plan['practical_exercise']}")
                md.append(f"- **Completion Criteria:** {plan['completion_criteria']}\n")

            return PlainTextResponse(content="\n".join(md), media_type="text/markdown")
        else:
            return report
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
