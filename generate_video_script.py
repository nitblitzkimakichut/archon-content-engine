import json
import argparse
from typing import Dict, Any

# Import our agents
from agents.content_strategy_agent import ContentStrategyAgent, VideoData, ContentAnalysisRequest
from agents.content_scriptwriter_agent import ContentScriptwriterAgent, ScriptRequest

def generate_script_from_analysis(analysis_data: Dict[str, Any], platform: str = "all") -> Dict[str, Any]:
    """Generate a video script from content analysis data"""
    # Create script request from analysis data
    request = ScriptRequest(
        hook_patterns=analysis_data.get("hook_patterns", []),
        format_trends=analysis_data.get("format_trends", []),
        engagement_tactics=analysis_data.get("engagement_tactics", []),
        content_themes=analysis_data.get("content_themes", []),
        summary=analysis_data.get("summary", ""),
        platform=platform
    )
    
    # Initialize scriptwriter agent and generate script
    agent = ContentScriptwriterAgent()
    result = agent.generate_script(request)
    
    return result.dict()

async def analyze_and_generate(video_file: str, platform: str = "all") -> Dict[str, Any]:
    """Analyze videos and generate a script based on the analysis"""
    # Load videos from JSON file
    with open(video_file, 'r') as f:
        video_data = json.load(f)
    
    # Create video objects
    videos = [VideoData(**video) for video in video_data]
    
    # Create analysis request
    request = ContentAnalysisRequest(videos=videos)
    
    # Initialize analysis agent and analyze videos
    analysis_agent = ContentStrategyAgent()
    analysis_result = await analysis_agent.analyze_videos(videos)
    
    # Generate script from analysis
    script_result = generate_script_from_analysis(analysis_result.dict(), platform)
    
    return {
        "analysis": analysis_result.dict(),
        "script": script_result
    }

def main():
    parser = argparse.ArgumentParser(description='Generate optimized short-form video scripts based on viral content analysis')
    parser.add_argument('--file', '-f', type=str, help='Path to JSON file containing video data')
    parser.add_argument('--analysis', '-a', type=str, help='Path to JSON file containing existing analysis data')
    parser.add_argument('--platform', '-p', type=str, default="all", choices=["tiktok", "youtube_shorts", "instagram_reels", "all"], help='Target platform for the script')
    parser.add_argument('--output', '-o', type=str, help='Path to save results (optional)')
    
    args = parser.parse_args()
    
    if not args.file and not args.analysis:
        print("Please provide either a video data file (--file) or an analysis file (--analysis)")
        return
    
    # If analysis file is provided, use it directly
    if args.analysis:
        with open(args.analysis, 'r') as f:
            analysis_data = json.load(f)
        
        # Check if this is raw video data or analysis data
        if isinstance(analysis_data, list) and all(isinstance(item, dict) and 'title' in item for item in analysis_data):
            # This is raw video data, not analysis
            print("Converting raw video data to analysis...")
            import asyncio
            videos = [VideoData(**video) for video in analysis_data]
            analysis_agent = ContentStrategyAgent()
            analysis_result = asyncio.run(analysis_agent.analyze_videos(videos))
            analysis_data = analysis_result.dict()
            print("Analysis complete.")
        
        script_result = generate_script_from_analysis(analysis_data, args.platform)
        result = {
            "analysis": analysis_data,
            "script": script_result
        }
    
    # Otherwise, analyze videos and generate script
    else:
        import asyncio
        result = asyncio.run(analyze_and_generate(args.file, args.platform))
    
    # Pretty print the script
    script = result["script"]
    
    print("\n===== GENERATED SCRIPT =====")
    print(f"\nTITLE: {script['title']}")
    print(f"\nHOOK TYPE: {script['hook_type']}")
    print(f"\nTHEME: {script['theme']}")
    print(f"\nESTIMATED DURATION: {script['estimated_duration']} seconds")
    print("\nSCRIPT:")
    print("--------")
    print(script['script'])
    print("--------")
    print(f"\nCTA: {script['cta']}")
    print("\nNOTES:")
    for note in script['notes']:
        print(f"- {note}")
    
    # Save results if output path is provided
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()
