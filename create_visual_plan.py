import json
import argparse
from typing import Dict, Any

# Import our agents
from agents.content_strategy_agent import ContentStrategyAgent, VideoData, ContentAnalysisRequest
from agents.content_scriptwriter_agent import ContentScriptwriterAgent, ScriptRequest
from agents.visual_content_planner_agent import VisualContentPlannerAgent, VisualPlanRequest

def create_visual_plan(script_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a visual plan from script data"""
    # Create visual plan request
    request = VisualPlanRequest(
        script=script_data.get("script", ""),
        hook=script_data.get("title", None),  # Use title as hook if available
        cta=script_data.get("cta", None),
        niche=script_data.get("theme", None),  # Use theme as niche if available
        tone="engaging and informative",  # Default tone
        platform=script_data.get("platform", "TikTok")
    )
    
    # Initialize visual planner agent and create plan
    agent = VisualContentPlannerAgent()
    result = agent.create_visual_plan(request)
    
    return result.dict()

def main():
    parser = argparse.ArgumentParser(description='Create visual production plans for short-form video scripts')
    parser.add_argument('--script', '-s', type=str, help='Path to JSON file containing script data')
    parser.add_argument('--output', '-o', type=str, help='Path to save visual plan (optional)')
    parser.add_argument('--platform', '-p', type=str, default="TikTok", 
                        choices=["TikTok", "Instagram", "YouTube"], 
                        help='Target platform for the visual plan')
    parser.add_argument('--demo', '-d', action='store_true', help='Run with demo data')
    
    args = parser.parse_args()
    
    if args.demo:
        # Use demo data
        script_data = {
            "script": "They said this kitchen was a lost cause. But $3,000 and 6 weekends later? It's now our favorite room.",
            "title": "You won't believe this transformation.",
            "cta": "Follow for more budget renovation ideas.",
            "theme": "home renovation",
            "platform": args.platform
        }
    elif args.script:
        # Load script data from file
        with open(args.script, 'r') as f:
            script_data = json.load(f)
            
        # Add platform if not present
        if "platform" not in script_data:
            script_data["platform"] = args.platform
    else:
        print("Please provide a script file (--script) or use demo data (--demo)")
        return
    
    # Create visual plan
    visual_plan = create_visual_plan(script_data)
    
    # Pretty print the visual plan
    print("\n===== VISUAL CONTENT PLAN =====\n")
    print(f"TITLE: {visual_plan['title']}\n")
    print(f"TOTAL DURATION: {visual_plan['total_duration']}\n")
    print(f"VOICEOVER: {visual_plan['voiceover_style']}\n")
    print(f"MUSIC: {visual_plan['music_recommendation']}\n")
    
    print("SCENES:")
    for i, scene in enumerate(visual_plan['scenes']):
        print(f"\nSCENE {i+1}: {scene['timestamp']}")
        print(f"TEXT: {scene['script_segment']}")
        print(f"STOCK FOOTAGE: {', '.join(scene['stock_footage'])}")
        if scene.get('text_overlay'):
            print(f"TEXT OVERLAY: {scene['text_overlay']}")
        print(f"VISUAL EFFECTS: {', '.join(scene['visual_effects'])}")
        print(f"TRANSITION: {scene['transition']}")
    
    print("\nSTOCK FOOTAGE SOURCES:")
    for source in visual_plan['stock_footage_platforms']:
        print(f"- {source}")
    
    print("\nEDITING TIPS:")
    for tip in visual_plan['editing_tips']:
        print(f"- {tip}")
    
    # Save results if output path is provided
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(visual_plan, f, indent=2)
        print(f"\nVisual plan saved to {args.output}")

if __name__ == "__main__":
    main()
