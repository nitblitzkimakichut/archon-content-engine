from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn
import json
import asyncio

# Import our agents
from agents.content_strategy_agent import ContentStrategyAgent, VideoData, ContentAnalysisRequest
from agents.content_scriptwriter_agent import ContentScriptwriterAgent, ScriptRequest
from agents.visual_content_planner_agent import VisualContentPlannerAgent, VisualPlanRequest

# Enhanced VideoData model with niche-specific fields
class EnhancedVideoData(VideoData):
    problem: Optional[str] = None
    audience: Optional[str] = None
    solution: Optional[str] = None
    emotional_triggers: Optional[str] = None
    niche: Optional[str] = None
    sub_niche: Optional[str] = None
    pain_points: Optional[str] = None
    value_proposition: Optional[str] = None

# Enhanced request model
class EnhancedContentAnalysisRequest(ContentAnalysisRequest):
    videos: List[EnhancedVideoData]
    target_niche: Optional[str] = None
    target_problem: Optional[str] = None
    target_audience: Optional[str] = None

app = FastAPI(
    title="TitanFlow Content Strategy AI",
    description="API for creating viral short-form video content from analysis to visual production plans",
    version="1.0.0"
)
# In content_strategy_api.py
if __name__ == "__main__":
    uvicorn.run("content_strategy_api:app", host="0.0.0.0", port=8000, reload=True)
# Initialize our agents
content_agent = ContentStrategyAgent()
scriptwriter_agent = ContentScriptwriterAgent()
visual_planner_agent = VisualContentPlannerAgent()

@app.get("/")
async def root():
    return {"message": "Welcome to TitanFlow Content Strategy AI", 
            "endpoints": ["/analyze", "/generate-script", "/create-visual-plan", "/full-pipeline", "/niche-analysis"]}

@app.post("/analyze", response_model=Dict[str, Any])
async def analyze_videos(request: ContentAnalysisRequest = Body(...)):
    """
    Analyze a list of viral videos and extract structured insights.
    
    The analysis includes:
    - Hook patterns (types and examples)
    - Format trends
    - Engagement tactics
    - Content themes
    - Overall summary
    """
    try:
        result = await content_agent.process_request(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/niche-analysis", response_model=Dict[str, Any])
async def analyze_niche_videos(request: EnhancedContentAnalysisRequest = Body(...)):
    """
    Analyze videos with enhanced niche-specific data.
    
    This endpoint accepts additional fields like problem, audience, solution, etc.
    and can filter analysis based on target niche, problem, or audience.
    """
    try:
        # Filter videos by target parameters if provided
        filtered_videos = request.videos
        
        if request.target_niche:
            filtered_videos = [v for v in filtered_videos if v.niche and request.target_niche.lower() in v.niche.lower()]
        
        if request.target_problem:
            filtered_videos = [v for v in filtered_videos if v.problem and request.target_problem.lower() in v.problem.lower()]
            
        if request.target_audience:
            filtered_videos = [v for v in filtered_videos if v.audience and request.target_audience.lower() in v.audience.lower()]
        
        # Create standard request with filtered videos
        standard_request = ContentAnalysisRequest(
            videos=[VideoData(
                title=v.title,
                description=v.description,
                views=v.views,
                publishedAt=v.publishedAt,
                channel=v.channel
            ) for v in filtered_videos],
            analysis_type=request.analysis_type
        )
        
        # Process with standard agent
        result = await content_agent.process_request(standard_request)
        
        # Add niche-specific insights
        result["niche_insights"] = {
            "problems": list(set([v.problem for v in filtered_videos if v.problem])),
            "audiences": list(set([v.audience for v in filtered_videos if v.audience])),
            "solutions": list(set([v.solution for v in filtered_videos if v.solution])),
            "emotional_triggers": list(set([v.emotional_triggers for v in filtered_videos if v.emotional_triggers])),
            "niches": list(set([v.niche for v in filtered_videos if v.niche])),
            "sub_niches": list(set([v.sub_niche for v in filtered_videos if v.sub_niche])),
            "pain_points": list(set([v.pain_points for v in filtered_videos if v.pain_points])),
            "value_propositions": list(set([v.value_proposition for v in filtered_videos if v.value_proposition]))
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Niche analysis failed: {str(e)}")

@app.post("/generate-script", response_model=Dict[str, Any])
async def generate_script(request: ScriptRequest = Body(...)):
    """
    Generate an optimized short-form video script based on content analysis data.
    
    The script includes:
    - Hook
    - Main content
    - Call to action
    - Metadata (estimated duration, hook type, theme)
    """
    try:
        result = scriptwriter_agent.generate_script(request)
        return result.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Script generation failed: {str(e)}")

@app.post("/create-visual-plan", response_model=Dict[str, Any])
async def create_visual_plan(request: VisualPlanRequest = Body(...)):
    """
    Create a detailed visual production plan from a short-form video script.
    
    The plan includes:
    - Scene breakdowns with timestamps
    - Stock footage suggestions
    - Text overlay recommendations
    - Visual effects and transitions
    - Voiceover and music guidance
    - Platform-specific editing tips
    """
    try:
        result = visual_planner_agent.create_visual_plan(request)
        return result.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual plan creation failed: {str(e)}")

@app.post("/full-pipeline", response_model=Dict[str, Any])
async def full_pipeline(videos: List[Dict[str, Any]] = Body(...), platform: str = Body("TikTok"), target_niche: Optional[str] = Body(None), target_problem: Optional[str] = Body(None)):
    """
    Run the complete content creation pipeline:
    1. Analyze viral videos
    2. Generate an optimized script
    3. Create a detailed visual production plan
    
    Returns the results from all three stages.
    """
    try:
        # Step 1: Analyze videos
        video_data = []
        for video in videos:
            # Create VideoData or EnhancedVideoData based on available fields
            if any(key in video for key in ["problem", "audience", "solution", "niche"]):
                video_data.append(EnhancedVideoData(**video))
            else:
                video_data.append(VideoData(**video))
        
        # Use niche-specific analysis if enhanced data is available
        if any(isinstance(v, EnhancedVideoData) for v in video_data):
            analysis_request = EnhancedContentAnalysisRequest(
                videos=video_data, 
                analysis_type="full",
                target_niche=target_niche,
                target_problem=target_problem
            )
            analysis_result = await analyze_niche_videos(analysis_request)
        else:
            analysis_request = ContentAnalysisRequest(videos=video_data, analysis_type="full")
            analysis_result = await content_agent.process_request(analysis_request)
        
        # Step 2: Generate script
        script_request = ScriptRequest(
            hook_patterns=analysis_result.get("hook_patterns", []),
            format_trends=analysis_result.get("format_trends", []),
            engagement_tactics=analysis_result.get("engagement_tactics", []),
            content_themes=analysis_result.get("content_themes", []),
            summary=analysis_result.get("summary", ""),
            platform=platform
        )
        
        # Add niche insights if available
        if "niche_insights" in analysis_result:
            script_request.niche_insights = analysis_result["niche_insights"]
        
        script_result = scriptwriter_agent.generate_script(script_request)
        
        # Step 3: Create visual plan
        visual_request = VisualPlanRequest(
            script=script_result.script,
            hook=script_result.title,
            cta=script_result.cta,
            niche=script_result.theme,
            tone="engaging and informative",
            platform=platform
        )
        visual_result = visual_planner_agent.create_visual_plan(visual_request)
        
        # Return all results
        return {
            "analysis": analysis_result,
            "script": script_result.dict(),
            "visual_plan": visual_result.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

@app.get("/sample")
async def get_sample_request():
    """
    Returns sample request formats for all endpoints
    """
    sample_videos = [
        {
            "title": "5 Morning Habits That Changed My Life",
            "description": "I tried these 5 morning habits for 30 days and here's what happened...",
            "views": 1500000,
            "publishedAt": "2023-05-15",
            "channel": "ProductivityGuru"
        },
        {
            "title": "You've Been Charging Your Phone Wrong",
            "description": "This simple trick will make your battery last twice as long!",
            "views": 2300000,
            "publishedAt": "2023-06-02",
            "channel": "TechHacks"
        }
    ]
    
    sample_analysis = {
        "hook_patterns": [
            {"type": "shock-based", "example": "You're doing this wrong — here's why."},
            {"type": "question-based", "example": "What if I told you this one habit could change your life?"}
        ],
        "format_trends": [
            "Hook → Insight → Visual Demo → CTA",
            "Fast-paced cuts with meme overlays and subtitles"
        ],
        "engagement_tactics": [
            "Open loops (e.g., 'Wait for it...')",
            "Direct CTAs ('Follow me for more')"
        ],
        "content_themes": [
            "Time management hacks",
            "Exposing common myths"
        ],
        "summary": "The most effective viral videos use fast-paced editing with captions and B-roll, lead with a curiosity or pain-point hook, and close with direct CTAs."
    }
    
    sample_script = {
        "script": "I can't believe I didn't know this behind-the-scenes secret sooner.\n\nWe all struggle with having too much to do and too little time. [show overwhelmed person]\n\nHere's a simple system that changed everything for me: [cut to notebook] The 1-3-5 Rule. Each day, commit to accomplishing: 1 big thing, 3 medium things, and 5 small things. [show list] That's it. This prevents overwhelm while still ensuring progress on what matters. [show completed list]\n\nStitch this with your results!",
        "hook": "I can't believe I didn't know this behind-the-scenes secret sooner.",
        "cta": "Stitch this with your results!",
        "niche": "productivity",
        "tone": "informative",
        "platform": "TikTok"
    }
    
    return {
        "analyze_endpoint": {
            "videos": sample_videos,
            "analysis_type": "full"
        },
        "generate_script_endpoint": sample_analysis,
        "create_visual_plan_endpoint": sample_script,
        "full_pipeline_endpoint": {
            "videos": sample_videos,
            "platform": "TikTok"
        }
    }

if __name__ == "__main__":
    uvicorn.run("content_strategy_api:app", host="0.0.0.0", port=8000, reload=True)
